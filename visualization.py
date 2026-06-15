import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/lagoon_sales_cleaned.csv")

# food item that makes the most money - Total revenue (total money)
item_sales = df.groupby("Food_Item")["Total_Sales"].sum().sort_values() #Index food item
item_sales.plot(
    kind="barh",
    color=[
        "#264653", "#2A9D8F", "#8AB17D", "#A7C957",
        "#E9C46A", "#F4A261", "#E76F51", "#D62828",
        "#6D597A", "#B56576", "#355070", "#457B9D",
        "#1D3557"])
plt.tight_layout()
plt.show()


# Average sales per food item - Average revenue
mean_sales = df.groupby("Food_Item")["Total_Sales"].mean().sort_values()
mean_sales.plot(kind="barh", title="Mean Sales per Food Item")
plt.xlabel("Average Sales")
plt.tight_layout()
plt.show()


#Date Total Sales
daily_sales = df.groupby("Date")["Total_Sales"].sum()
daily_sales.plot(kind="line", marker="o", title="Daily Sales Trend")
plt.xlabel("Date")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# category na maraming nabenta
cat_sales = df.groupby("Food_Category")["Total_Sales"].sum()
cat_sales.plot(kind="pie", autopct="%1.2f%%", title="What Category Sells the Most")
plt.show()

# time of day na maraming benta
hour_sales = df.groupby("Time")["Total_Sales"].sum().sort_index()
hour_sales.plot(kind="line", marker="o", title="What Time of Day is Busiest") #May circle sa kada point
plt.xlabel("Hour of Day")
plt.ylabel("Total Sales")
plt.show()

#mabenta vs di mabenta
item_sales = df.groupby("Food_Item")["Total_Sales"].sum()
print("Lowest:", item_sales.idxmin(), item_sales.min())
print("Highest:", item_sales.idxmax(), item_sales.max())
plt.show()

#FOR STOCK LELELELEELELEL
stock_change = df.groupby("Food_Item")[["Stock_Before","Stock_After"]].mean()
stock_change.plot(kind="bar", title="Average Stock Levels per Item")
plt.show()