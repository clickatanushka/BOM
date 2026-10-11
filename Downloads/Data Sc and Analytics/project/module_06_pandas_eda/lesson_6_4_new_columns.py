"""Video 6.4 - New columns, apply, pd.cut
Run: python module_06_pandas_eda/lesson_6_4_new_columns.py"""

import pandas as pd

from module_06_pandas_eda.cleaning import add_columns, add_details, clean_orders, load_raw


def order_size(revenue):
    if revenue >= 5000:
        return "Big"
    elif revenue >= 1000:
        return "Medium"
    return "Small"


pd.set_option("display.width", 200, "display.max_columns", None)
orders, customers, products = load_raw()
df = clean_orders(orders)   # the 6.3 steps (the notebook loads orders_clean.csv instead)
print(df.shape, df["order_date"].dtype)

print("\n== 1. Revenue - one line for 5,000 rows ==")
df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)
print(df[["order_id", "quantity", "unit_price", "discount", "revenue"]].head())
print("Total revenue 2025: ₹", round(df["revenue"].sum(), 2))
print("Average order value: ₹", round(df["revenue"].mean(), 2))

print("\n== 2. Profit - needs the cost price from products ==")
# A map lookup (like XLOOKUP); video 6.6 does this properly with merge
unit_cost = df["product_id"].map(products.set_index("product_id")["cost_price"])
df["profit"] = (df["revenue"] - df["quantity"] * unit_cost).round(2)
print("Total profit: ₹", round(df["profit"].sum(), 2))
print("Loss-making orders:", (df["profit"] < 0).sum())

print("\n== 3. Date parts with .dt ==")
df["order_month"] = df["order_date"].dt.month
df["month_name"] = df["order_date"].dt.month_name()
df["weekday"] = df["order_date"].dt.day_name()
print(df[["order_date", "order_month", "month_name", "weekday"]].head())

print("\n== 4. apply: run your own function on every row ==")
df["order_size"] = df["revenue"].apply(order_size)
print(df["order_size"].value_counts())
df["is_returned"] = (df["returned"] == "Y").astype(int)   # a yes/no column needs no apply
print("Return rate:", round(df["is_returned"].mean() * 100, 1), "%")

print("\n== 5. pd.cut: turn ages into groups ==")
print(customers["age"].min(), customers["age"].max())
# bins (17,25], (25,35], ... - the right edge is included
customers["age_group"] = pd.cut(customers["age"], bins=[17, 25, 35, 45, 60],
                                labels=["18-25", "26-35", "36-45", "46-60"])
print(customers["age_group"].value_counts().sort_index())
print(customers[["customer_id", "name", "age", "age_group"]].head())

print("\n== Practice ==")
df["delivery_speed"] = pd.cut(df["delivery_days"], bins=[0, 3, 5, 20], labels=["Fast", "Normal", "Slow"])
print(df["delivery_speed"].value_counts())

print("\n== The same three columns, packaged as a function ==")
cols = ["revenue", "profit", "order_month"]
packaged = add_columns(add_details(clean_orders(orders), customers, products))
pd.testing.assert_frame_equal(df[cols].reset_index(drop=True), packaged[cols],
                              check_exact=False, atol=0.01)   # profit here is rounded to paise
print("add_columns() gives the same revenue, profit and order_month as the steps above")
