import pandas as pd

def analyze_dataset(file_path):
    df = pd.read_csv(file_path)

    # Normalize column names: strip spaces, replace spaces with underscores
    df.columns = df.columns.str.strip().str.replace(' ', '_')

    results = {}

    # 1. Total revenue
    results["total_revenue"] = df["Total_Sales"].sum()

    # 2. Average sales per transaction
    results["average_sales"] = df["Total_Sales"].mean()

    # 3. Total quantity sold
    results["total_quantity_sold"] = df["Quantity_Sold"].sum()

    # 4. Best-selling food item by quantity
    results["best_selling_food"] = df.groupby("Type_of_Food")["Quantity_Sold"].sum().sort_values(ascending=False)

    # 5. Highest earning food item by total sales
    results["highest_earning_food"] = df.groupby("Type_of_Food")["Total_Sales"].sum().sort_values(ascending=False)

    # 6. Sales by food category
    results["sales_by_category"] = df.groupby("Food_Category")["Total_Sales"].sum().sort_values(ascending=False)

    # 7. Sales by stall
    results["sales_by_stall"] = df.groupby("Stall_Number")["Total_Sales"].sum().sort_values(ascending=False)

    # 8. Payment method breakdown
    results["payment_method_breakdown"] = df["Payment_Method"].value_counts()

    # 9. Customer type breakdown
    results["customer_type_breakdown"] = df["Customer_Type"].value_counts()

    # 10. Sales by day
    results["sales_by_day"] = df.groupby("Day")["Total_Sales"].sum()

    # 11. Low stock records
    results["low_stock"] = df[df["Stock_After"] <= 10][
        ["Date", "Stall_Number", "Type_of_Food", "Stock_After"]
    ]

    return results