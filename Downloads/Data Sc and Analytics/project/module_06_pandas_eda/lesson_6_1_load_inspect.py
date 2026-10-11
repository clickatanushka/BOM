"""Video 6.1 - DataFrames: load and inspect
Run: python module_06_pandas_eda/lesson_6_1_load_inspect.py"""

import pandas as pd

from project_paths import CUSTOMERS, ORDERS_RAW, PRODUCTS

pd.set_option("display.width", 200, "display.max_columns", None)

print("\n== 1. Import pandas and load the files ==")
orders = pd.read_csv(ORDERS_RAW)
customers = pd.read_csv(CUSTOMERS)
products = pd.read_csv(PRODUCTS)

print("\n== 2. First look: head() and tail() ==")
print(orders.head())
print(orders.tail(3))

print("\n== 3. How big? shape and columns ==")
print("orders:", orders.shape)
print("customers:", customers.shape)
print("products:", products.shape)
print(list(orders.columns))
# 5,055 order rows - but ShopKart had 5,000 orders in 2025. Remember that.

print("\n== 4. Column types: info() ==")
orders.info()
# unit_price and order_date are text; discount, payment_mode and rating have gaps.

print("\n== 5. Number summary: describe() ==")
print(orders.describe())
# quantity: 75% is 2 but the max is 99. Suspicious.
print(orders["quantity"].value_counts().sort_index())

print("\n== 6. Missing values: isnull().sum() ==")
print(orders.isnull().sum())

print("\n== 7. Text columns: how many spellings? ==")
print("Distinct city spellings:", orders["city"].nunique())
print(orders["city"].value_counts())
print(orders["payment_mode"].value_counts(dropna=False))
print(orders["returned"].value_counts())
print("Duplicate rows:", orders.duplicated().sum())
print(orders.loc[orders["unit_price"].str.contains("₹"), "unit_price"].head())
print(orders.loc[orders["order_date"].str.contains(r"^\d{2}-"), "order_date"].head())

print("\n== 8. The other two tables look clean ==")
print(customers.isnull().sum().sum(), "missing values in customers")
print(products.isnull().sum().sum(), "missing values in products")
print(customers.head())
print(products["category"].value_counts())

# To-do for 6.3: 55 duplicates | 27 city spellings | unit_price text | two date formats
# | blank discount/payment_mode, "upi" | Yes/No vs Y/N | quantity 99 | blank rating (real: not rated)

print("\n== Practice ==")
print(customers["membership"].value_counts())
print(products.sort_values("list_price").iloc[[0, -1]][["product_name", "list_price"]])
