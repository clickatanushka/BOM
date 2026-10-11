"""Video 6.5 - groupby and pivot_table
Run: python module_06_pandas_eda/lesson_6_5_groupby_pivot.py"""

import pandas as pd

from module_06_pandas_eda.cleaning import clean_orders, load_raw

pd.set_option("display.width", 200, "display.max_columns", None)
df = clean_orders(load_raw()[0])   # the 6.3 steps, plus the 6.4 columns we need
df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)
df["order_month"] = df["order_date"].dt.month
df["is_returned"] = (df["returned"] == "Y").astype(int)
print(df.shape)

print("\n== 1. value_counts: how many of each ==")
print(df["city"].value_counts())
print(df["payment_mode"].value_counts(normalize=True).round(3) * 100)

print("\n== 2. groupby: split -> apply -> combine ==")
print(df.groupby("city")["revenue"].sum().sort_values(ascending=False).round(0))

print("\n== 3. Several numbers at once with agg ==")
city_summary = df.groupby("city").agg(
    orders=("order_id", "count"),
    revenue=("revenue", "sum"),
    avg_order=("revenue", "mean"),
    avg_rating=("rating", "mean"),
    return_rate=("is_returned", "mean"),
).round(2).sort_values("revenue", ascending=False)
print(city_summary)
print("Overall return rate:", round(df["is_returned"].mean() * 100, 1), "%")
print("Pune return rate:", round(df.loc[df["city"] == "Pune", "is_returned"].mean() * 100, 1), "%")

print("\n== 4. Group by two columns ==")
print(df.groupby(["city", "payment_mode"])["is_returned"].mean().round(3).head(12))

print("\n== 5. pivot_table: the Excel pivot table in one line ==")
print(pd.pivot_table(df, index="city", columns="payment_mode", values="revenue",
                     aggfunc="sum", margins=True, margins_name="Total").round(0))
print(df.groupby("order_month")["revenue"].sum().round(0))
print(pd.pivot_table(df, index="payment_mode", values="is_returned", aggfunc=["mean", "count"]).round(3))

print("\n== Practice ==")
print(df.groupby("payment_mode")["delivery_days"].mean().round(2).sort_values(ascending=False))
print(pd.pivot_table(df, index="city", columns="returned", values="rating", aggfunc="mean").round(2))
