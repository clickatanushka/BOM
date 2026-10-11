"""Video 6.2 - Select, filter and sort
Run: python module_06_pandas_eda/lesson_6_2_select_filter_sort.py"""

import pandas as pd

from project_paths import ORDERS_RAW

pd.set_option("display.width", 200, "display.max_columns", None)
orders = pd.read_csv(ORDERS_RAW)   # the RAW file on purpose, to show why cleaning matters

print("\n== 1. Selecting columns ==")
print(orders["city"].head())                                                  # one column -> Series
print(orders[["order_id", "city", "payment_mode", "delivery_days"]].head())   # double brackets -> DataFrame

print("\n== 2. Selecting rows: loc (by label/condition) and iloc (by position) ==")
print(orders.iloc[0])
print(orders.loc[0:2, ["order_id", "quantity"]])   # loc includes the end label 2

print("\n== 3. Filtering with a condition ==")
cod = orders[orders["payment_mode"] == "COD"]
print(len(cod), "COD orders")
print(cod.head())
print(len(orders[orders["delivery_days"] >= 8]), "orders took 8+ days")
# & = AND, | = OR, and each condition needs its own brackets
slow_cod = orders[(orders["delivery_days"] >= 8) & (orders["payment_mode"] == "COD")]
print(len(slow_cod), "slow COD orders")
print((orders["returned"] == "Y").sum(), "rows say Y")
print(orders["returned"].isin(["Y", "Yes"]).sum(), "rows say Y or Yes")

print("\n== 4. Why cleaning matters: filter for Delhi ==")
print("city == 'Delhi':", (orders["city"] == "Delhi").sum())
print("all Delhi spellings:", orders["city"].str.strip().str.lower().isin(["delhi", "new delhi"]).sum())

print("\n== 5. Sorting ==")
print(orders.sort_values("delivery_days", ascending=False)[["order_id", "city", "delivery_days", "rating"]].head())
print(orders.sort_values(["city", "rating"], ascending=[True, False])[["order_id", "city", "rating"]].head())
print(orders.nlargest(8, "quantity")[["order_id", "product_id", "quantity", "unit_price"]])
# The 10s are Smartphones (real); the 99s are typos - fixed in 6.3.

print("\n== Practice ==")
print((orders["rating"] == 1).sum())
print(orders[(orders["payment_mode"] == "Net Banking") & (orders["delivery_days"] == 2)].tail())
