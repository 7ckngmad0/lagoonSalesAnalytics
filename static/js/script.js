// Helper function to show alerts
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    const container = document.getElementById('alertContainer');
    container.innerHTML = alertHtml;
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

// Helper to format currency
function formatCurrency(amount) {
    return '₱' + parseFloat(amount).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// File upload handler
document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        showAlert('Uploading file...', 'info');
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        // Update file info
        document.getElementById('fileName').textContent = data.data.file_name;
        document.getElementById('fileRows').textContent = data.data.rows.toLocaleString();
        document.getElementById('fileCols').textContent = data.data.columns;
        document.getElementById('fileInfoCard').style.display = 'block';

        document.getElementById('cleanDataBtn').disabled = false;
        document.getElementById('showDatasetInfoBtn').disabled = false;
        document.getElementById('showRawDataBtn').disabled = false;
        showAlert('File uploaded successfully!', 'success');
    } catch (error) {
        showAlert('Error uploading file: ' + error.message, 'danger');
    }
});

// Clean data handler
document.getElementById('cleanDataBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        showAlert('Cleaning data...', 'info');

        const response = await fetch('/api/clean-data', { method: 'POST' });
        const data = await response.json();

        if (!response.ok) throw new Error(data.error);

        document.getElementById('originalRows').textContent = data.original_rows.toLocaleString();
        document.getElementById('cleanedRows').textContent = data.cleaned_rows.toLocaleString();
        document.getElementById('removedRows').textContent = data.removed_rows.toLocaleString();
        document.getElementById('cleaningInfoCard').style.display = 'block';
        document.getElementById('downloadBtn').disabled = false;
        document.getElementById('showCleanedDataBtn').disabled = false;
        document.getElementById('generateChartsBtn').disabled = false;

        showAlert('Data cleaned successfully!', 'success');
        loadAnalysis();
    } catch (error) {
        showAlert('Error cleaning data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Load analysis
async function loadAnalysis() {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';

        // Load metrics
        const analysisResponse = await fetch('/api/analyze');
        const analysisData = await analysisResponse.json();
        if (!analysisResponse.ok) throw new Error(analysisData.error);

        // Load chart data
        const chartResponse = await fetch('/api/chart-data');
        const chartData = await chartResponse.json();
        if (!chartResponse.ok) throw new Error(chartData.error);

        // Update metrics
        document.getElementById('totalRevenue').textContent = formatCurrency(analysisData.total_revenue);
        document.getElementById('avgSales').textContent = formatCurrency(analysisData.average_sales);
        document.getElementById('totalQty').textContent = Math.round(analysisData.total_quantity_sold).toLocaleString();
        
        // Count total transactions
        const totalTransactions = Object.keys(analysisData.best_selling_food).length;
        document.getElementById('totalTrans').textContent = totalTransactions.toLocaleString();

        document.getElementById('metricsContainer').style.display = 'block';

        // Render charts
        renderCharts(chartData);

        // Render top items
        renderTopItems(analysisData);
        document.getElementById('topItemsContainer').style.display = 'block';

        document.getElementById('chartsContainer').style.display = 'block';
    } catch (error) {
        showAlert('Error loading analysis: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
}

// Render charts
function renderCharts(data) {
    // Map chart names to image element IDs
    const chartMapping = {
        'sales_by_food': 'foodItemChart',
        'sales_by_category': 'categoryChart',
        'sales_by_stall': 'stallChart',
        'payment_methods': 'paymentChart',
        'customer_types': 'customerChart',
        'sales_by_day': 'dayChart'
    };

    // Load chart images
    for (const [chartName, elementId] of Object.entries(chartMapping)) {
        const element = document.getElementById(elementId);
        if (data[chartName]) {
            element.src = data[chartName];
        }
    }
}

// Render top items
function renderTopItems(data) {
    // Best selling items
    const bestSellingList = document.getElementById('bestSellingList');
    bestSellingList.innerHTML = '';
    const bestSelling = data.best_selling_food;
    const bestItems = Object.entries(bestSelling).sort((a,b) => b[1] - a[1]).slice(0, 5); 
    bestItems.forEach(([item, qty], index) => {
        const badge = `<span class="badge bg-${['danger', 'warning', 'info', 'success', 'secondary'][index] || 'secondary'} me-2">#${index + 1}</span>`;
        bestSellingList.innerHTML += `
            <div class="d-flex justify-content-between mb-2">
                <span>${badge}${item}</span>
                <span class="fw-bold">${Math.round(qty)} units</span>
            </div>
        `;
    });

    // Highest earning items
    const highestEarningList = document.getElementById('highestEarningList');
    highestEarningList.innerHTML = '';
    const highestEarning = data.highest_earning_food;
    const topEarning = Object.entries(highestEarning).sort((a, b) => b[1] - a[1]).slice(0, 5);
    topEarning.forEach(([item, amount], index) => {
        const badge = `<span class="badge bg-${['danger', 'warning', 'info', 'success', 'secondary'][index] || 'secondary'} me-2">#${index + 1}</span>`;
        highestEarningList.innerHTML += `
            <div class="d-flex justify-content-between mb-2">
                <span>${badge}${item}</span>
                <span class="fw-bold">${formatCurrency(amount)}</span>
            </div>
        `;
    });

    //Highest Day Sales 
    const highestDaySale = document.getElementById('highestDaySale');
    highestDaySale.innerHTML = '';
    const highestDay = data.sales_by_day;
    const topDay = Object.entries(highestDay).sort((a, b) => b[1] - a[1]).slice(0, 5);
    topDay.forEach(([day, amount], index) => {
        const badge = `<span class="badge bg-${['danger', 'warning', 'info', 'success', 'secondary'][index] || 'secondary'} me-2">#${index + 1}</span>`;
        highestDaySale.innerHTML += `
            <div class="d-flex justify-content-between mb-2">
                <span>${badge}${day}</span>
                <span class="fw-bold">${formatCurrency(amount)}</span>
            </div>
        `;
    });

    //Highest Earning Stall
    const highestEarningStall = document.getElementById('highestEarningStall');
    highestEarningStall.innerHTML = '';
    const highestEarner = data.sales_by_stall;
    const topEarner = Object.entries(highestEarner).sort((a, b) => b[1] - a[1]).slice(0, 5);
    topEarner.forEach(([stall, amount], index) => {
        const badge = `<span class="badge bg-${['danger', 'warning', 'info', 'success', 'secondary'][index] || 'secondary'} me-2">#${index + 1}</span>`;
        highestEarningStall.innerHTML += `
            <div class="d-flex justify-content-between mb-2">
                <span>${badge}${stall}</span>
                <span class="fw-bold">${formatCurrency(amount)}</span>
            </div>
        `;
    });
}

// Download cleaned data
document.getElementById('downloadBtn').addEventListener('click', async () => {
    try {
        const response = await fetch('/api/download-cleaned');
        if (!response.ok) throw new Error('Download failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
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

// Load sample data
document.getElementById('sampleBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        showAlert('Loading sample data...', 'info');

        const response = await fetch('/api/sample-data');
        const data = await response.json();

        if (!response.ok) throw new Error(data.error);

        document.getElementById('fileName').textContent = data.data.file_name;
        document.getElementById('fileRows').textContent = data.data.rows.toLocaleString();
        document.getElementById('fileCols').textContent = data.data.columns;
        document.getElementById('fileInfoCard').style.display = 'block';
        document.getElementById('cleanDataBtn').disabled = false;
        document.getElementById('showDatasetInfoBtn').disabled = false;
        document.getElementById('showRawDataBtn').disabled = false;

        showAlert('Sample data loaded successfully! Click "Clean Data" to proceed.', 'success');
    } catch (error) {
        showAlert('Error loading sample data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Hide all main content sections
function hideAllSections() {
    document.getElementById('datasetInfoContainer').style.display = 'none';
    document.getElementById('rawDataContainer').style.display = 'none';
    document.getElementById('cleanedDataContainer').style.display = 'none';
    document.getElementById('metricsContainer').style.display = 'none';
    document.getElementById('chartsContainer').style.display = 'none';
    document.getElementById('topItemsContainer').style.display = 'none';
}

// Show Dataset Info
document.getElementById('showDatasetInfoBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();
        
        const response = await fetch('/api/dataset-info');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        // Update dataset info
        document.getElementById('datasetTotalRows').textContent = data.rows.toLocaleString();
        document.getElementById('datasetTotalCols').textContent = data.columns;
        document.getElementById('datasetFileName').textContent = data.file_name;
        document.getElementById('datasetMemory').textContent = data.memory_usage;

        // Render column details
        const columnDetails = document.getElementById('columnDetailsContainer');
        columnDetails.innerHTML = '';
        const cols = Object.entries(data.column_info);
        cols.forEach(([colName, colInfo]) => {
            columnDetails.innerHTML += `
                <div class="mb-3 p-2 border rounded">
                    <strong>${colName}</strong>
                    <div class="small text-muted">
                        Type: ${colInfo.type} | Non-null: ${colInfo.non_null} | Unique: ${colInfo.unique}
                    </div>
                </div>
            `;
        });

        document.getElementById('datasetInfoContainer').style.display = 'block';
        showAlert('Dataset information loaded!', 'success');
    } catch (error) {
        showAlert('Error loading dataset info: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Show Raw Data
document.getElementById('showRawDataBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();
        
        const response = await fetch('/api/raw-data');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        renderDataTable('raw', data.data, data.columns);
        document.getElementById('rawDataContainer').style.display = 'block';
        document.getElementById('rawDataRowCount').textContent = `Rows: ${data.data.length.toLocaleString()}`;
        showAlert('Raw data loaded!', 'success');
    } catch (error) {
        showAlert('Error loading raw data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Show Cleaned Data
document.getElementById('showCleanedDataBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();
        
        const response = await fetch('/api/cleaned-data');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        renderDataTable('cleaned', data.data, data.columns);
        document.getElementById('cleanedDataContainer').style.display = 'block';
        document.getElementById('cleanedDataRowCount').textContent = `Rows: ${data.data.length.toLocaleString()}`;
        showAlert('Cleaned data loaded!', 'success');
    } catch (error) {
        showAlert('Error loading cleaned data: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Generate Charts
document.getElementById('generateChartsBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        showAlert('Generating charts...', 'info');

        const response = await fetch('/api/generate-charts', { method: 'POST' });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        showAlert('Charts generated successfully! Click "Show Charts" to view.', 'success');
        document.getElementById('showChartsBtn').disabled = false;
    } catch (error) {
        showAlert('Error generating charts: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Show Charts
document.getElementById('showChartsBtn').addEventListener('click', async () => {
    try {
        document.getElementById('loadingSpinner').style.display = 'block';
        hideAllSections();
        
        const response = await fetch('/api/chart-data');
        const data = await response.json();
        if (!response.ok) throw new Error(data.error);

        renderCharts(data);
        document.getElementById('chartsContainer').style.display = 'block';
        document.getElementById('topItemsContainer').style.display = 'block';
        showAlert('Charts loaded!', 'success');
    } catch (error) {
        showAlert('Error loading charts: ' + error.message, 'danger');
    } finally {
        document.getElementById('loadingSpinner').style.display = 'none';
    }
});

// Render data table
function renderDataTable(type, rows, columns) {
    const headId = `${type}DataHead`;
    const bodyId = `${type}DataBody`;
    const searchId = `${type}DataSearch`;

    const head = document.getElementById(headId);
    const body = document.getElementById(bodyId);
    const searchInput = document.getElementById(searchId);

    // Create header
    head.innerHTML = '<tr>' + columns.map(col => `<th>${col}</th>`).join('') + '</tr>';

    // Function to render body with filter
    function renderBody(filteredRows) {
        body.innerHTML = '';
        filteredRows.forEach(row => {
            const cells = columns.map(col => {
                let value = row[col];
                if (typeof value === 'number') {
                    value = value.toFixed(2);
                }
                return `<td>${value || '-'}</td>`;
            }).join('');
            body.innerHTML += `<tr>${cells}</tr>`;
        });
    }

    renderBody(rows);

    // Search functionality
    searchInput.addEventListener('keyup', (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = rows.filter(row => {
            return columns.some(col => {
                const value = String(row[col]).toLowerCase();
                return value.includes(query);
            });
        });
        renderBody(filtered);
    });
}
