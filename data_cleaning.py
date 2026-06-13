import pandas as pd

def clean_dataset(file_path):
    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip().str.replace(" ", "_")

    df = df.drop_duplicates()

    text_columns = [
        "Transaction_ID",
        "Day",
        "Time",
        "Type_of_Food",
        "Food_Category",
        "Payment_Method",
        "Customer_Type"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    if "Type_of_Food" in df.columns:
        df = df.rename(columns={"Type_of_Food": "Food_Item"})

    if "Food_Item" in df.columns:
        df["Food_Item"] = df["Food_Item"].replace({
            "SIsig": "Sisig",
            "SIomai Rice": "Siomai Rice",
            "siomai rice": "Siomai Rice",
            "sisig": "Sisig",
            "FEWA Burger" : "Fewa Burger"
        })

    if "Payment_Method" in df.columns:
        df["Payment_Method"] = df["Payment_Method"].replace({
            "gcash": "GCash",
            "GCASH": "GCash",
            "Gcash": "GCash",
            "cash": "Cash",
            "CASH": "Cash",
            "maya": "Maya",
            "MAYA": "Maya"
        })

        df["Payment_Method"] = df["Payment_Method"].replace("nan", pd.NA)
        df["Payment_Method"] = df["Payment_Method"].fillna("Unknown")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")

    number_columns = [
        "Stall_Number",
        "Quantity_Sold",
        "Unit_Price",
        "Total_Sales",
        "Stock_Before",
        "Stock_After"
    ]

    for col in number_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[df["Quantity_Sold"] > 0]
    df = df[df["Unit_Price"] > 0]

    df["Total_Sales"] = df["Quantity_Sold"] * df["Unit_Price"]

    output_path = "data/lagoon_sales_cleaned.csv"
    df.to_csv(output_path, index=False)

    return df