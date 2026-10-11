"""Video 6.6 - Merge with products and customers
Run: python module_06_pandas_eda/lesson_6_6_merge.py"""

import pandas as pd

from module_06_pandas_eda.cleaning import (add_columns, add_details, clean_orders, final_checks,
                                           load_raw, save_clean)
from project_paths import REFERENCE_CLEAN_CSV

pd.set_option("display.width", 200, "display.max_columns", None)
raw, customers, products = load_raw()
orders = clean_orders(raw)
print(orders.shape, products.shape, customers.shape)

print("\n== merge = SQL JOIN ==")
# orders LEFT JOIN products ON product_id -> orders.merge(products, on="product_id", how="left")
# Lookup keys must be unique, or the merge would double rows
print("Duplicate product_ids:", products["product_id"].duplicated().sum())
print("Duplicate customer_ids:", customers["customer_id"].duplicated().sum())

df = orders.merge(products[["product_id", "product_name", "category", "cost_price"]],
                  on="product_id", how="left")
print(df.shape)
df = df.merge(customers[["customer_id", "gender", "age", "membership"]],
              on="customer_id", how="left")
print(df.shape)
assert len(df) == 5000, "Row count changed - check the join keys!"
print("Rows with no product match:", df["category"].isnull().sum())
print("Rows with no customer match:", df["membership"].isnull().sum())

pd.testing.assert_frame_equal(df, add_details(orders, customers, products))
print("add_details() gives the same table as the two merges above")

print("\n== Add the calculated columns (from 6.4) and save ==")
df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)
df["profit"] = df["revenue"] - df["quantity"] * df["cost_price"]
df["order_month"] = df["order_date"].dt.month
print(df.shape)
print(list(df.columns))
print(df.head())

pd.testing.assert_frame_equal(df, add_columns(add_details(orders, customers, products)))
print("add_columns() gives the same columns as the three lines above")

path = save_clean(df)
print("Saved", path.name, df.shape)

print("\n== Final checks ==")
checks = final_checks(df)
for name, ok in checks.items():
    print("OK  " if ok else "FAIL", name)
assert all(checks.values()), "A final check failed!"

# assert_frame_equal ignores the 1e-12 float noise in profit
saved = pd.read_csv(path, parse_dates=["order_date"])
pd.testing.assert_frame_equal(saved, pd.read_csv(REFERENCE_CLEAN_CSV, parse_dates=["order_date"]))
print("shopkart_clean.csv matches the course reference file")
print(f"Total revenue: ₹{df['revenue'].sum():,.2f} | Total profit: ₹{df['profit'].sum():,.2f}")

print("\n== What merge did NOT include: customers who never ordered ==")
check = customers.merge(orders[["customer_id"]].drop_duplicates(), on="customer_id",
                        how="left", indicator=True)   # left_only = never ordered
print(check["_merge"].value_counts())

print("\n== Practice ==")
print(df.groupby("category")[["revenue", "profit"]].sum().round(0).sort_values("profit", ascending=False))
