import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Ensure charts directory exists
CHARTS_DIR = 'static/charts'
os.makedirs(CHARTS_DIR, exist_ok=True)

def clear_charts():
    """Clear all existing charts"""
    for file in os.listdir(CHARTS_DIR):
        if file.endswith('.png'):
            os.remove(os.path.join(CHARTS_DIR, file))

def generate_charts(df):
    """Generate all charts from dataframe and save to static/charts"""
    if df is None or len(df) == 0:
        return {}
    
    clear_charts()
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    color_palette = ['#800000', '#FFD700', '#5A0000', '#1f77b4', '#ff7f0e']
    
    chart_paths = {}
    
    # 1. Sales by Food Item
    if 'Food_Item' in df.columns and 'Total_Sales' in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            sales_by_food = df.groupby('Food_Item')['Total_Sales'].sum().sort_values(ascending=True).tail(10)
            sales_by_food.plot(kind='barh', ax=ax, color=color_palette[0])
            ax.set_xlabel('Total Sales (₱)', fontsize=12)
            ax.set_ylabel('Food Item', fontsize=12)
            ax.set_title('Top 10 Sales by Food Item', fontsize=14, fontweight='bold')
            plt.tight_layout()
            chart_paths['sales_by_food'] = f'{CHARTS_DIR}/sales_by_food.png'
            plt.savefig(chart_paths['sales_by_food'], dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating sales_by_food chart: {e}")
    
    # 2. Sales by Category
    if 'Food_Category' in df.columns and 'Total_Sales' in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            sales_by_category = df.groupby('Food_Category')['Total_Sales'].sum().sort_values(ascending=False)
            colors_cat = color_palette[:len(sales_by_category)]
            ax.pie(sales_by_category.values, labels=sales_by_category.index, autopct='%1.1f%%', 
                   colors=colors_cat, startangle=90)
            ax.set_title('Sales Distribution by Category', fontsize=14, fontweight='bold')
            plt.tight_layout()
            chart_paths['sales_by_category'] = f'{CHARTS_DIR}/sales_by_category.png'
            plt.savefig(chart_paths['sales_by_category'], dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating sales_by_category chart: {e}")
    
    # 3. Sales by Stall
    if 'Stall_Number' in df.columns and 'Total_Sales' in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            sales_by_stall = df.groupby('Stall_Number')['Total_Sales'].sum().sort_values(ascending=False)
            stall_labels = [f'Stall {int(s)}' for s in sales_by_stall.index]
            ax.bar(stall_labels, sales_by_stall.values, color=color_palette[1])
            ax.set_xlabel('Stall Number', fontsize=12)
            ax.set_ylabel('Total Sales (₱)', fontsize=12)
            ax.set_title('Sales by Stall', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_paths['sales_by_stall'] = f'{CHARTS_DIR}/sales_by_stall.png'
            plt.savefig(chart_paths['sales_by_stall'], dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating sales_by_stall chart: {e}")
    
    # 4. Payment Method Distribution
    if 'Payment_Method' in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            payment_dist = df['Payment_Method'].value_counts()
            colors_pay = color_palette[:len(payment_dist)]
            ax.bar(payment_dist.index, payment_dist.values, color=colors_pay)
            ax.set_xlabel('Payment Method', fontsize=12)
            ax.set_ylabel('Count', fontsize=12)
            ax.set_title('Payment Method Distribution', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_paths['payment_methods'] = f'{CHARTS_DIR}/payment_methods.png'
            plt.savefig(chart_paths['payment_methods'], dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating payment_methods chart: {e}")
    
    # 5. Customer Type Distribution
    if 'Customer_Type' in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            customer_dist = df['Customer_Type'].value_counts()
            colors_cust = color_palette[:len(customer_dist)]
            ax.pie(customer_dist.values, labels=customer_dist.index, autopct='%1.1f%%',
                   colors=colors_cust, startangle=90)
            ax.set_title('Customer Type Distribution', fontsize=14, fontweight='bold')
            plt.tight_layout()
            chart_paths['customer_types'] = f'{CHARTS_DIR}/customer_types.png'
            plt.savefig(chart_paths['customer_types'], dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating customer_types chart: {e}")
    
    # 6. Sales by Day
    if 'Day' in df.columns and 'Total_Sales' in df.columns:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            sales_by_day = df.groupby('Day')['Total_Sales'].sum()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            sales_by_day = sales_by_day.reindex([d for d in day_order if d in sales_by_day.index])
            ax.plot(sales_by_day.index, sales_by_day.values, marker='o', linewidth=2, 
                    markersize=8, color=color_palette[2])
            ax.fill_between(range(len(sales_by_day)), sales_by_day.values, alpha=0.3, 
                            color=color_palette[2])
            ax.set_xlabel('Day of Week', fontsize=12)
            ax.set_ylabel('Total Sales (₱)', fontsize=12)
            ax.set_title('Sales by Day of Week', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_paths['sales_by_day'] = f'{CHARTS_DIR}/sales_by_day.png'
            plt.savefig(chart_paths['sales_by_day'], dpi=100, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error generating sales_by_day chart: {e}")
    
    return chart_paths
