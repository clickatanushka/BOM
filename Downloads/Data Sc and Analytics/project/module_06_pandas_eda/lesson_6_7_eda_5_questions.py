"""Video 6.7 - EDA walkthrough: 5 business questions
Run: python module_06_pandas_eda/lesson_6_7_eda_5_questions.py"""

import matplotlib.pyplot as plt
import pandas as pd

from module_06_pandas_eda.cleaning import build_clean_table, load_raw
from project_paths import module_output

pd.set_option("display.width", 200, "display.max_columns", None)
df = build_clean_table(*load_raw())   # same table as shopkart_clean.csv
df["is_returned"] = (df["returned"] == "Y").astype(int)
print(df.shape)
print("Total revenue: ₹", round(df["revenue"].sum()))
print("Total profit: ₹", round(df["profit"].sum()))
print("Overall return rate:", round(df["is_returned"].mean() * 100, 1), "%")

print("\n== Q1. Which month was best? ==")
monthly = df.groupby("order_month")["revenue"].sum().round(0)
print(monthly)
print("Best month:", monthly.idxmax(), "with ₹", monthly.max())
print("Worst month:", monthly.idxmin(), "with ₹", monthly.min())
ax = monthly.plot(kind="bar", title="ShopKart revenue by month (₹)", figsize=(8, 3))
ax.get_figure().savefig(module_output("module_06") / "revenue_by_month.png", dpi=150, bbox_inches="tight")
if plt.get_backend().lower() != "agg":   # Agg (MPLBACKEND=Agg, tests) has no window and warns
    plt.show()
# Finding 1: October best (₹19.78 lakh), November almost tied (₹19.66 lakh), May weakest (₹7.87 lakh).

print("\n== Q2. Which city brings the most revenue? ==")
city = df.groupby("city").agg(revenue=("revenue", "sum"), orders=("order_id", "count"),
                              avg_order=("revenue", "mean")).round(0).sort_values("revenue", ascending=False)
city["share_%"] = (city["revenue"] / city["revenue"].sum() * 100).round(1)
print(city)
# Finding 2: Delhi, Bengaluru and Mumbai bring about 45%. Ahmedabad has the highest average order (₹3,515).

print("\n== Q3. Which category has the highest return rate? ==")
cat = df.groupby("category").agg(orders=("order_id", "count"), returns=("is_returned", "sum"),
                                 return_rate=("is_returned", "mean"), revenue=("revenue", "sum")
                                 ).sort_values("return_rate", ascending=False)
cat["return_rate"] = (cat["return_rate"] * 100).round(1)
print(cat.round(0))
print((df.groupby("city")["is_returned"].mean() * 100).round(1).sort_values(ascending=False).head(3))
# Finding 3: Fashion 21.0% vs 13.7% overall. Pune 32.4% - no other city is above 14.3%.

print("\n== Q4. Do discounts make people buy more, or rate higher? ==")
print(df.groupby("discount").agg(orders=("order_id", "count"), avg_quantity=("quantity", "mean"),
                                 avg_rating=("rating", "mean")).round(2))
print("Correlation discount vs quantity:", round(df["discount"].corr(df["quantity"]), 2))
print("Correlation discount vs rating:  ", round(df["discount"].corr(df["rating"]), 2))
# Finding 4: quantity rises with discount, rating stays flat. Correlation is not causation.

print("\n== Q5. Prime vs Free members ==")
mem = df.groupby("membership").agg(orders=("order_id", "count"), customers=("customer_id", "nunique"),
                                   revenue=("revenue", "sum"), avg_order=("revenue", "mean"),
                                   return_rate=("is_returned", "mean")).round(2)
mem["orders_per_customer"] = (mem["orders"] / mem["customers"]).round(1)
mem["revenue_per_customer"] = (mem["revenue"] / mem["customers"]).round(0)
print(mem)
# Finding 5: same spend per order, but Prime customers order about twice as often (9.8 vs 4.8).
