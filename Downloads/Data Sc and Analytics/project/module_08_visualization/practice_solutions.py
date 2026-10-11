"""Video 8.2-8.3 (practice) - Module 8 practice solutions
Run: python module_08_visualization/practice_solutions.py"""

import matplotlib.pyplot as plt

from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import GREY, HIGHLIGHT, MAIN, save_and_show

MODULE = "module_08"

df = load_clean()

print("\n== Task 1 - Which payment mode is used most? ==")
pay = df["payment_mode"].value_counts().sort_values()
fig = plt.figure(figsize=(7, 4))
plt.barh(pay.index, pay.values, color=MAIN)
plt.title(f"UPI is the top payment mode ({pay['UPI'] / len(df) * 100:.0f}% of orders)")
plt.xlabel("Number of orders")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_practice1_payment_modes.png")
print(pay.sort_values(ascending=False))

print("\n== Task 2 - Monthly profit trend ==")
mp = df.groupby("order_month")["profit"].sum() / 100000
fig = plt.figure(figsize=(8, 4))
plt.plot(mp.index, mp.values, marker="o", color=MAIN)
plt.ylim(0, mp.max() * 1.15)
plt.xticks(range(1, 13))
plt.title(f"Profit peaks in month {mp.idxmax()}")
plt.xlabel("Month")
plt.ylabel("Profit (₹ lakh)")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_practice2_monthly_profit.png")
print("Highest-profit month:", mp.idxmax(), "with ₹", round(mp.max(), 2), "lakh")

print("\n== Task 3 - Age of customers per order ==")
fig = plt.figure(figsize=(7, 4))
plt.hist(df["age"], bins=20, color=MAIN, edgecolor="white")
plt.title("Most orders come from customers in their late 20s and early 30s")
plt.xlabel("Age")
plt.ylabel("Orders")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_practice3_age_histogram.png")
print("Median age:", df["age"].median(), "| middle 50%:", df["age"].quantile(0.25), "to", df["age"].quantile(0.75))

print("\n== Task 4 - Does payment mode affect returns? ==")
rr = (df["returned"].eq("Y").groupby(df["payment_mode"]).mean() * 100).sort_values()
fig = plt.figure(figsize=(7, 4))
plt.barh(rr.index, rr.values, color=[HIGHLIGHT if v == rr.max() else GREY for v in rr.values])
plt.title(f"{rr.idxmax()} orders are returned most often ({rr.max():.1f}%)")
plt.xlabel("Return rate (%)")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_practice4_returns_by_payment.png")
print(rr.round(1).sort_values(ascending=False))

print("\n== Task 5 - Rewrite the titles as message titles ==")
# 1. "Revenue by Category"   2. "Orders by Membership"
cat_share = df.groupby("category")["revenue"].sum() / df["revenue"].sum() * 100
mem = df.groupby("membership").agg(orders=("order_id", "count"), customers=("customer_id", "nunique"))
mem["orders_per_customer"] = (mem["orders"] / mem["customers"]).round(1)
print(f"1. Electronics brings {cat_share['Electronics']:.0f}% of all revenue")
times = mem.loc["Prime", "orders_per_customer"] / mem.loc["Free", "orders_per_customer"]
print(f"2. Prime customers order about {times:.0f}x as often as Free customers")
print(mem)
