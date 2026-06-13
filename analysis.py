import pandas as pd

def analyze_dataset(file_path):
    df = pd.read_csv(file_path)

    results = {}

    # 1. Total revenue
    results["total_revenue"] = df["Total_Sales"].sum()

    # 2. Average sales per transaction
    results["average_sales"] = df["Total_Sales"].mean()

    # 3. Total quantity sold
    results["total_quantity_sold"] = df["Quantity_Sold"].sum()

    # 4. Best-selling food item by quantity
    best_selling_food = df.groupby("Food_Item")["Quantity_Sold"].sum().sort_values(ascending=False)
    results["best_selling_food"] = best_selling_food

    # 5. Highest earning food item by total sales
    highest_earning_food = df.groupby("Food_Item")["Total_Sales"].sum().sort_values(ascending=False)
    results["highest_earning_food"] = highest_earning_food

    # 6. Sales by food category
    sales_by_category = df.groupby("Food_Category")["Total_Sales"].sum().sort_values(ascending=False)
    results["sales_by_category"] = sales_by_category

    # 7. Sales by stall
    sales_by_stall = df.groupby("Stall_Number")["Total_Sales"].sum().sort_values(ascending=False)
    results["sales_by_stall"] = sales_by_stall

    # 8. Most used payment method
    payment_method_count = df["Payment_Method"].value_counts()
    results["payment_method_count"] = payment_method_count

    # 9. Customer type count
    customer_type_count = df["Customer_Type"].value_counts()
    results["customer_type_count"] = customer_type_count

    # 10. Sales by day
    sales_by_day = df.groupby("Day")["Total_Sales"].sum().sort_values(ascending=False)
    results["sales_by_day"] = sales_by_day

    # 11. Low stock records
    low_stock = df[df["Stock_After"] <= 10][
        ["Date", "Stall_Number", "Food_Item", "Stock_After"]
    ]
    results["low_stock"] = low_stock

    return results
