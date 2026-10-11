"""Video Module 6 practice - EDA practice: 8 open questions (solutions)
Run: python module_06_pandas_eda/practice_solutions.py"""

import pandas as pd

from module_06_pandas_eda.cleaning import build_clean_table, load_raw

pd.set_option("display.width", 200, "display.max_columns", None)
df = build_clean_table(*load_raw())   # same table as shopkart_clean.csv
df["is_returned"] = (df["returned"] == "Y").astype(int)
print(df.shape)

print("\n== Q1. Top 5 products by revenue ==")
print(df.groupby("product_name")["revenue"].sum().sort_values(ascending=False).round(0).head(5))
# Finding: Tablet (₹25.22 lakh) and Smartphone (₹19.69 lakh) far ahead; Air Fryer third.

print("\n== Q2. Which category has the best profit margin? ==")
cat = df.groupby("category")[["revenue", "profit"]].sum()
cat["margin_%"] = (cat["profit"] / cat["revenue"] * 100).round(1)
print(cat.sort_values("margin_%", ascending=False))
# Finding: Beauty 42.8%, Fashion 36.2%. Electronics brings half the revenue but keeps 11.0%.

print("\n== Q3. Delivery time vs rating ==")
print(df.groupby("delivery_days")["rating"].mean().round(2))
print("Correlation:", round(df["delivery_days"].corr(df["rating"]), 2))
# Finding: rating drops from ~4.2 at 2-3 days to ~3 at 8-9 days (correlation -0.33).

print("\n== Q4. Is COD riskier? Return rate by payment mode ==")
print((df.groupby("payment_mode")["is_returned"].mean() * 100).round(1).sort_values(ascending=False))
# Finding: COD returns most (19.1%); prepaid modes around 12-13%.

print("\n== Q5. Which age group spends the most per order? ==")
df["age_group"] = pd.cut(df["age"], bins=[17, 25, 35, 45, 60], labels=["18-25", "26-35", "36-45", "46-60"])
print(df.groupby("age_group", observed=True).agg(orders=("order_id", "count"),
                                                 avg_order=("revenue", "mean")).round(0))
# Finding: 26-35 place half of all orders (2,494); 26-45 spend the most per order (~₹3,000).

print("\n== Q6. Men vs women: order value and return rate ==")
print(df.groupby("gender").agg(orders=("order_id", "count"), avg_order=("revenue", "mean"),
                               return_rate=("is_returned", "mean")).round(3))
# Finding: small gaps (₹3,024 vs ₹2,872; 14.4% vs 13.2%) - not worth a strategy without testing.

print("\n== Q7. In Pune, is the return problem in every category? ==")
pune = df[df["city"] == "Pune"]
print((pune.groupby("category")["is_returned"].mean() * 100).round(1).sort_values(ascending=False))
# Finding: every Pune category is 20.7% (Books) to 38.8% (Fashion) - the problem is the city.

print("\n== Q8. Which weekday gets the most orders? ==")
df["weekday"] = df["order_date"].dt.day_name()
print(df["weekday"].value_counts())
# Finding: Sunday is busiest (782); other days 675-721. Months matter far more than weekdays.
