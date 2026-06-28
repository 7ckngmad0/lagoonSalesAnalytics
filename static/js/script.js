// ─── State ───────────────────────────────────────────────────────────────────
// Stores the analysis data fetched after cleaning, so Generate Charts can use it
let cachedAnalysisData = null;

// Track Chart.js instances so we can destroy before re-rendering
const chartInstances = {};

// ─── Helpers ─────────────────────────────────────────────────────────────────
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    const container = document.getElementById('alertContainer');
    container.innerHTML = alertHtml;
    setTimeout(() => { container.innerHTML = ''; }, 5000);
}

function formatCurrency(amount) {
    return '₱' + parseFloat(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// ─── Section visibility ───────────────────────────────────────────────────────
function hideAllSections() {
    ['datasetInfoContainer', 'rawDataContainer', 'cleanedDataContainer',
     'metricsContainer', 'chartsContainer', 'topItemsContainer']
        .forEach(id => document.getElementById(id).style.display = 'none');
}

// ─── Table renderers ──────────────────────────────────────────────────────────
function renderDataTable(type, rows, columns) {
    const head = document.getElementById(`${type}DataHead`);
    const body = document.getElementById(`${type}DataBody`);
    const searchInput = document.getElementById(`${type}DataSearch`);

    head.innerHTML = '<tr>' + columns.map(col => `<th>${col}</th>`).join('') + '</tr>';

    function renderBody(filteredRows) {
        body.innerHTML = '';
        filteredRows.forEach(row => {
            const cells = columns.map(col => {
                let value = row[col];
                if (typeof value === 'number') value = value.toFixed(2);
                return `<td>${value ?? '-'}</td>`;
            }).join('');
            body.innerHTML += `<tr>${cells}</tr>`;
        });
    }

    renderBody(rows);

    // Remove old listener to avoid duplicates
    const freshInput = searchInput.cloneNode(true);
    searchInput.parentNode.replaceChild(freshInput, searchInput);
    freshInput.addEventListener('keyup', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = rows.filter(row =>
            columns.some(col => String(row[col]).toLowerCase().includes(query))
        );
        renderBody(filtered);
    });
}

// ─── Chart rendering (Chart.js – dynamic, based on CSV data) ─────────────────
function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

const MAROON  = 'rgba(128, 0, 0, 0.85)';
const GOLD    = 'rgba(255, 215, 0, 0.85)';
const PALETTE = [
    '#800000','#FFD700','#B22222','#DAA520','#8B0000',
    '#CD853F','#A0522D','#D2691E','#DC143C','#C0392B'
];

function renderCharts(analysisData) {
    // ── 1. Sales by Food Item (Top 10) – horizontal bar ──────────────────────
    destroyChart('foodItemChart');
    const foodEntries = Object.entries(analysisData.best_selling_food)
        .sort((a, b) => b[1] - a[1]).slice(0, 10);
    chartInstances['foodItemChart'] = new Chart(
        document.getElementById('foodItemChart'),
        {
            type: 'bar',
            data: {
                labels: foodEntries.map(([k]) => k),
                datasets: [{
                    label: 'Units Sold',
                    data: foodEntries.map(([, v]) => Math.round(v)),
                    backgroundColor: PALETTE
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                plugins: { legend: { display: false } }
            }
        }
    );

    // ── 2. Sales by Category – pie ────────────────────────────────────────────
    destroyChart('categoryChart');
    const catEntries = Object.entries(analysisData.sales_by_category || {});
    if (catEntries.length) {
        chartInstances['categoryChart'] = new Chart(
            document.getElementById('categoryChart'),
            {
                type: 'pie',
                data: {
                    labels: catEntries.map(([k]) => k),
                    datasets: [{
                        data: catEntries.map(([, v]) => parseFloat(v)),
                        backgroundColor: PALETTE
                    }]
                },
                options: { responsive: true }
            }
        );
    }

    // ── 3. Sales by Stall – bar ───────────────────────────────────────────────
    destroyChart('stallChart');
    const stallEntries = Object.entries(analysisData.sales_by_stall || {})
        .sort((a, b) => b[1] - a[1]);
    if (stallEntries.length) {
        chartInstances['stallChart'] = new Chart(
            document.getElementById('stallChart'),
            {
                type: 'bar',
                data: {
                    labels: stallEntries.map(([k]) => `Stall ${k}`),
                    datasets: [{
                        label: 'Revenue (₱)',
                        data: stallEntries.map(([, v]) => parseFloat(v)),
                        backgroundColor: MAROON
                    }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false } }
                }
            }
        );
    }

    // ── 4. Payment Methods – doughnut ─────────────────────────────────────────
    destroyChart('paymentChart');
    const payEntries = Object.entries(analysisData.payment_method_breakdown || {});
    if (payEntries.length) {
        chartInstances['paymentChart'] = new Chart(
            document.getElementById('paymentChart'),
            {
                type: 'doughnut',
                data: {
                    labels: payEntries.map(([k]) => k),
                    datasets: [{
                        data: payEntries.map(([, v]) => parseFloat(v)),
                        backgroundColor: PALETTE
                    }]
                },
                options: { responsive: true }
            }
        );
    }

    // ── 5. Customer Types – pie ───────────────────────────────────────────────
    destroyChart('customerChart');
    const custEntries = Object.entries(analysisData.customer_type_breakdown || {});
    if (custEntries.length) {
        chartInstances['customerChart'] = new Chart(
            document.getElementById('customerChart'),
            {
                type: 'pie',
                data: {
                    labels: custEntries.map(([k]) => k),
                    datasets: [{
                        data: custEntries.map(([, v]) => parseFloat(v)),
                        backgroundColor: [MAROON, GOLD, '#B22222', '#DAA520']
                    }]
                },
                options: { responsive: true }
            }
        );
    }

    // ── 6. Sales by Day – line ────────────────────────────────────────────────
    destroyChart('dayChart');
    const dayOrder = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
    const dayData  = analysisData.sales_by_day || {};
    const orderedDays = dayOrder.filter(d => d in dayData);
    if (orderedDays.length) {
        chartInstances['dayChart'] = new Chart(
            document.getElementById('dayChart'),
            {
                type: 'line',
                data: {
                    labels: orderedDays,
                    datasets: [{
                        label: 'Revenue (₱)',
                        data: orderedDays.map(d => parseFloat(dayData[d])),
                        borderColor: MAROON,
                        backgroundColor: 'rgba(128,0,0,0.1)',
                        fill: true,
                        tension: 0.3,
                        pointBackgroundColor: GOLD
                    }]
                },
                options: { responsive: true }
            }
        );
    }
}

// ─── Top-items renderer ───────────────────────────────────────────────────────
function renderTopItems(data) {
    const colors = ['danger', 'warning', 'info', 'success', 'secondary'];

    function listHTML(entries, formatter) {
        return entries.map(([item, val], i) =>
            `<div class="d-flex justify-content-between mb-2">
                <span><span class="badge bg-${colors[i] || 'secondary'} me-2">#${i + 1}</span>${item}</span>
                <span class="fw-bold">${formatter(val)}</span>
             </div>`
        ).join('');
    }

    document.getElementById('bestSellingList').innerHTML = listHTML(
        Object.entries(data.best_selling_food).sort((a,b)=>b[1]-a[1]).slice(0,5),
        v => `${Math.round(v)} units`
    );
    document.getElementById('highestEarningList').innerHTML = listHTML(
        Object.entries(data.highest_earning_food).sort((a,b)=>b[1]-a[1]).slice(0,5),
        formatCurrency
    );
    document.getElementById('highestDaySale').innerHTML = listHTML(
        Object.entries(data.sales_by_day).sort((a,b)=>b[1]-a[1]).slice(0,5),
        formatCurrency
    );
    document.getElementById('highestEarningStall').innerHTML = listHTML(
        Object.entries(data.sales_by_stall).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([k,v])=>[`Stall ${k}`,v]),
        formatCurrency
    );
}

// ─── Event: File upload ───────────────────────────────────────────────────────
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        showAlert('Uploading file...', 'info');
        const response = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        document.getElementById('fileName').textContent    = data.data.file_name;
        document.getElementById('fileRows').textContent    = data.data.rows.toLocaleString();
        document.getElementById('fileCols').textContent    = data.data.columns;
        document.getElementById('fileInfoCard').style.display = 'block';

        // Only unlock buttons that make sense before cleaning
        document.getElementById('cleanDataBtn').disabled        = false;
        document.getElementById('showDatasetInfoBtn').disabled  = false;
        document.getElementById('showRawDataBtn').disabled      = false;

        showAlert('File uploaded successfully! Click "Clean Data" to proceed.', 'success');
    } catch (error) {
        showAlert('Error uploading file: ' + error.message, 'danger');
    }
});

// ─── Event: Load sample data ──────────────────────────────────────────────────
document.getElementById('sampleBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        showAlert('Loading sample data...', 'info');

        const response = await fetch('/api/sample-data');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        document.getElementById('fileName').textContent       = data.data.file_name;
        document.getElementById('fileRows').textContent       = data.data.rows.toLocaleString();
        document.getElementById('fileCols').textContent       = data.data.columns;
        document.getElementById('fileInfoCard').style.display = 'block';

        // Unlock pre-cleaning buttons
        document.getElementById('cleanDataBtn').disabled       = false;
        document.getElementById('showDatasetInfoBtn').disabled = false;
        document.getElementById('showRawDataBtn').disabled     = false;

        // Show a raw data preview so the user sees something happened
        const rawResp = await fetch('/api/raw-data');
        const rawData = await rawResp.json();
        if (rawResp.ok) {
            hideAllSections();
            renderDataTable('raw', rawData.data, rawData.columns);
            document.getElementById('rawDataContainer').style.display = 'block';
            document.getElementById('rawDataRowCount').textContent    = `Rows: ${rawData.total_rows.toLocaleString()}`;
        }

        showAlert('Sample data loaded! Click "Clean Data" to continue.', 'success');
    } catch (error) {
        showAlert('Error loading sample data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// ─── Event: Clean Data ────────────────────────────────────────────────────────
document.getElementById('cleanDataBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        showAlert('Cleaning data...', 'info');

        const response = await fetch('/api/clean-data', { method: 'POST' });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        // Show cleaning summary card
        document.getElementById('originalRows').textContent     = data.original_rows.toLocaleString();
        document.getElementById('cleanedRows').textContent      = data.cleaned_rows.toLocaleString();
        document.getElementById('removedRows').textContent      = data.removed_rows.toLocaleString();
        document.getElementById('cleaningInfoCard').style.display = 'block';

        // Unlock the rest of the navigation buttons
        document.getElementById('showCleanedDataBtn').disabled  = false;
        document.getElementById('generateChartsBtn').disabled   = false;
        document.getElementById('downloadBtn').disabled         = false;

        // ── Fetch and cache analysis data (metrics + chart source) ──────────
        const aResp = await fetch('/api/analyze');
        const aData = await aResp.json();
        if (!aResp.ok) throw new Error(aData.error);
        cachedAnalysisData = aData;

        // Show key metrics immediately after cleaning
        document.getElementById('totalRevenue').textContent = formatCurrency(aData.total_revenue);
        document.getElementById('avgSales').textContent     = formatCurrency(aData.average_sales);
        document.getElementById('totalQty').textContent     = Math.round(aData.total_quantity_sold).toLocaleString();
        document.getElementById('totalTrans').textContent   = Object.keys(aData.best_selling_food).length.toLocaleString();
        document.getElementById('metricsContainer').style.display = 'block';

        // Show cleaned data preview (no charts yet!)
        hideAllSections();
        document.getElementById('metricsContainer').style.display    = 'block';
        document.getElementById('cleanedDataContainer').style.display = 'block';
        renderDataTable('cleaned',
            data.preview.slice(0, 1000),
            Object.keys(data.preview[0] || {})
        );
        document.getElementById('cleanedDataRowCount').textContent = `Rows: ${data.cleaned_rows.toLocaleString()}`;

        showAlert('Data cleaned successfully! Use "Generate Charts" to create visualizations.', 'success');
    } catch (error) {
        showAlert('Error cleaning data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// ─── Event: Show Dataset Info ─────────────────────────────────────────────────
document.getElementById('showDatasetInfoBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();

        const response = await fetch('/api/dataset-info');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        document.getElementById('datasetTotalRows').textContent = data.rows.toLocaleString();
        document.getElementById('datasetTotalCols').textContent = data.columns;
        document.getElementById('datasetFileName').textContent  = data.file_name;
        document.getElementById('datasetMemory').textContent    = data.memory_usage;

        const columnDetails = document.getElementById('columnDetailsContainer');
        columnDetails.innerHTML = '';
        Object.entries(data.column_info).forEach(([colName, colInfo]) => {
            columnDetails.innerHTML += `
                <div class="mb-3 p-2 border rounded">
                    <strong>${colName}</strong>
                    <div class="small text-muted">
                        Type: ${colInfo.type} | Non-null: ${colInfo.non_null} | Unique: ${colInfo.unique}
                    </div>
                </div>`;
        });

        document.getElementById('datasetInfoContainer').style.display = 'block';
        showAlert('Dataset information loaded!', 'success');
    } catch (error) {
        showAlert('Error loading dataset info: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// ─── Event: Show Raw Data ─────────────────────────────────────────────────────
document.getElementById('showRawDataBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();

        const response = await fetch('/api/raw-data');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        renderDataTable('raw', data.data, data.columns);
        document.getElementById('rawDataContainer').style.display   = 'block';
        document.getElementById('rawDataRowCount').textContent       = `Rows: ${data.data.length.toLocaleString()}`;
        showAlert('Raw data loaded!', 'success');
    } catch (error) {
        showAlert('Error loading raw data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// ─── Event: Show Cleaned Data ─────────────────────────────────────────────────
document.getElementById('showCleanedDataBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();

        const response = await fetch('/api/cleaned-data');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        renderDataTable('cleaned', data.data, data.columns);
        document.getElementById('cleanedDataContainer').style.display = 'block';
        document.getElementById('cleanedDataRowCount').textContent     = `Rows: ${data.data.length.toLocaleString()}`;
        showAlert('Cleaned data loaded!', 'success');
    } catch (error) {
        showAlert('Error loading cleaned data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// ─── Event: Generate Charts ───────────────────────────────────────────────────
// This is where charts are created — ONLY when the user explicitly clicks this.
document.getElementById('generateChartsBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        showAlert('Generating charts...', 'info');

        // Make sure we have analysis data
        if (!cachedAnalysisData) {
            const aResp = await fetch('/api/analyze');
            const aData = await aResp.json();
            if (!aResp.ok) throw new Error(aData.error);
            cachedAnalysisData = aData;
        }

        hideAllSections();
        renderCharts(cachedAnalysisData);
        renderTopItems(cachedAnalysisData);

        document.getElementById('chartsContainer').style.display     = 'block';
        document.getElementById('topItemsContainer').style.display   = 'block';
        document.getElementById('showChartsBtn').disabled            = false;

        showAlert('Charts generated from your data!', 'success');
    } catch (error) {
        showAlert('Error generating charts: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// ─── Event: Show Charts (re-show already-generated charts) ───────────────────
document.getElementById('showChartsBtn').addEventListener('click', () => {
    if (!cachedAnalysisData) {
        showAlert('Please click "Generate Charts" first.', 'warning');
        return;
    }
    hideAllSections();
    // Charts are already rendered in the canvas elements; just show the containers
    document.getElementById('chartsContainer').style.display   = 'block';
    document.getElementById('topItemsContainer').style.display = 'block';
});

// ─── Event: Download cleaned CSV ──────────────────────────────────────────────
document.getElementById('downloadBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/download-cleaned');
        if (!response.ok) throw new Error('Download failed');

        const blob = await response.blob();
        const url  = window.URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href     = url;
        a.download = 'lagoon_sales_cleaned.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();

        showAlert('Data downloaded successfully!', 'success');
    } catch (error) {
        showAlert('Error downloading data: ' + error.message, 'danger');
    }
});