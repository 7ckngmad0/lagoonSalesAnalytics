# Lagoon Sales Analytics System - Web Version

A modern web-based analytics system for analyzing Lagoon Stalls sales data. Built with Flask, Bootstrap 5, and Chart.js.

## Features

- 📤 **File Upload**: Upload CSV files for analysis
- 🧹 **Data Cleaning**: Automated data cleaning and standardization
- 📊 **Visual Analytics**: Interactive charts and visualizations
  - Sales by food item, category, and stall
  - Payment method distribution
  - Customer type breakdown
  - Sales trends by day
- 📈 **Key Metrics**: Total revenue, average sales, quantity sold
- ⭐ **Top Performers**: Best-selling items and highest earning products
- 💾 **Export**: Download cleaned data as CSV

## Project Structure

```
lagoon_stalls_analysis_web/
├── app.py                 # Flask application
├── analysis.py           # Data analysis functions
├── data_cleaning.py      # Data cleaning and preprocessing
├── requirements.txt      # Python dependencies
├── data/                 # Data folder
│   ├── lagoon_sales_mock.csv      # Sample data
│   └── lagoon_sales_cleaned.csv   # Cleaned output
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Styling
    └── js/
        └── script.js     # Frontend logic
```

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Prepare Data Folder**:
   - Ensure `data/` folder exists with sample CSV files

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Open in Browser**:
   - Navigate to `http://localhost:5000`

3. **Using the App**:
   - Click "Load Sample Data" to test with sample data
   - Or upload your own CSV file
   - Click "Clean Data" to process the data
   - View analytics, charts, and metrics
   - Download cleaned data if needed

## API Endpoints

- `GET /` - Main application page
- `POST /api/upload` - Upload CSV file
- `POST /api/clean-data` - Clean the uploaded data
- `GET /api/analyze` - Get analysis metrics
- `GET /api/chart-data` - Get data for charts
- `GET /api/download-cleaned` - Download cleaned CSV
- `GET /api/sample-data` - Load sample data

## Data Requirements

Your CSV file should contain the following columns:
- `Date` - Transaction date
- `Transaction_ID` - Unique transaction identifier
- `Day` - Day of week
- `Time` - Time of transaction
- `Stall_Number` - Stall identifier
- `Type_of_Food` or `Food_Item` - Item name
- `Food_Category` - Category (e.g., Snacks, Meals)
- `Quantity_Sold` - Quantity sold
- `Unit_Price` - Price per unit
- `Total_Sales` - Total sales amount
- `Payment_Method` - Payment type (Cash, GCash, Maya)
- `Customer_Type` - Type of customer
- `Stock_Before` - Stock before transaction
- `Stock_After` - Stock after transaction

## Features in Detail

### Data Cleaning
- Removes duplicates
- Standardizes column names
- Fixes common spelling variations
- Normalizes payment methods
- Converts data types
- Calculates derived fields

### Analytics
- Total revenue calculation
- Average sales per transaction
- Total quantity metrics
- Best-selling items analysis
- Highest earning items
- Category-wise breakdown
- Stall performance comparison
- Payment method preferences
- Customer type distribution
- Daily sales trends
- Low stock alerts

### Visualizations
- Bar charts for item and stall performance
- Pie charts for category and payment distribution
- Line charts for sales trends
- Responsive design for all devices

## Customization

### Colors
Edit the color scheme in `static/css/style.css`:
- Maroon: `#800000`
- Dark Maroon: `#5A0000`
- Gold: `#FFD700`

### Data Format
Modify the cleaning rules in `data_cleaning.py` to match your CSV format.

## Troubleshooting

- **Port 5000 already in use**: Change the port in `app.py`: `app.run(port=5001)`
- **File upload errors**: Ensure CSV format is correct and file size < 16MB
- **Chart not showing**: Verify the required columns exist in your data

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Created for Polytechnic University of the Philippines
