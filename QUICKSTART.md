# Quick Start Guide - Lagoon Sales Analytics Web

## Steps to Run

### 1. Install Dependencies
```bash
cd c:\vscode\python\lagoon_stalls_analysis_web
pip install -r requirements.txt
```

### 2. Copy Sample Data (if available)
Copy `lagoon_sales_mock.csv` from the original folder to the `data/` folder:
```bash
copy ..\lagoon_stalls_analysis\data\lagoon_sales_mock.csv .\data\
```

### 3. Run the Application
```bash
python app.py
```

### 4. Access in Browser
Open: http://localhost:5000

### 5. Use the Application
- Click **"Load Sample Data"** to test
- Click **"Clean Data"** to process
- View all analytics and charts
- Download cleaned data with **"Download Cleaned"** button

## Key Features

✅ Upload CSV files  
✅ Automatic data cleaning  
✅ Interactive charts & visualizations  
✅ Key performance metrics  
✅ Export cleaned data  
✅ Responsive design  
✅ Real-time analysis  

## Requirements

- Python 3.7+
- Flask
- pandas
- Modern web browser

## Notes

- Max file upload: 16MB
- Server runs on: http://localhost:5000
- Press Ctrl+C to stop the server
- Data is processed in memory (not saved unless explicitly downloaded)

For more details, see README.md