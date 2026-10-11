"""Video 8.3 - Seaborn
Run: python module_08_visualization/lesson_8_3_seaborn.py"""

import warnings

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import HIGHLIGHT, MAIN, RETURN_COLORS, save_and_show

MODULE = "module_08"

# Seaborn takes the whole DataFrame and a column name and does the groupby for you.
df = load_clean()
# seaborn 0.13's boxplot passes matplotlib 3.11 an old argument (vert=) that it warns about - not our code.
warnings.filterwarnings("ignore", message="vert: bool was deprecated")
sns.set_theme(style="whitegrid")
print(df.shape)

print("\n== 1. countplot - how many orders in each category? ==")
fig = plt.figure(figsize=(8, 4))
order = df["category"].value_counts().index        # biggest first
sns.countplot(data=df, x="category", order=order, color=MAIN)
plt.title("Fashion has the most orders")
plt.xlabel("Category")
plt.ylabel("Number of orders")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_countplot.png")
print(df["category"].value_counts())

print("\n== 2. countplot with hue - returns per category ==")
fig = plt.figure(figsize=(8, 4))
sns.countplot(data=df, x="category", hue="returned", order=order, palette=RETURN_COLORS)
plt.title("Fashion also has the most returns")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_countplot_returns.png")
# The return RATE is easier to compare than raw counts:
print((df["returned"].eq("Y").groupby(df["category"]).mean() * 100).round(1).sort_values(ascending=False))

print("\n== 3. barplot - average revenue per order, by category ==")
# barplot shows the MEAN. The thin black line is the confidence interval (how sure we are).
fig = plt.figure(figsize=(8, 4))
sns.barplot(data=df, x="category", y="revenue", order=order, color=MAIN)
plt.title("An Electronics order is worth far more than other categories")
plt.ylabel("Average revenue per order (₹)")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_barplot.png")
print(df.groupby("category")["revenue"].mean().round(0).sort_values(ascending=False))

print("\n== 4. boxplot - are returned orders delivered more slowly? ==")
# Line in the box = median, box = middle 50% (IQR), dots = outliers (Module 3)
fig = plt.figure(figsize=(6, 4))
sns.boxplot(data=df, x="returned", y="delivery_days", hue="returned", palette=RETURN_COLORS, legend=False)
plt.title("Returned orders took longer to deliver")
plt.xlabel("Returned? (N = kept, Y = returned)")
plt.ylabel("Delivery days")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_boxplot.png")
print(df.groupby("returned")["delivery_days"].agg(["median", "mean"]).round(2))

print("\n== 5. scatterplot with hue - does a bigger discount mean people buy more? ==")
# Many orders share the same discount and quantity: a little random 'jitter' stops dots hiding each other.
rng = np.random.default_rng(42)
plot_df = df.copy()
plot_df["discount_jitter"] = plot_df["discount"] + rng.uniform(-0.01, 0.01, len(df))
plot_df["quantity_jitter"] = plot_df["quantity"] + rng.uniform(-0.2, 0.2, len(df))
fig = plt.figure(figsize=(8, 5))
sns.scatterplot(data=plot_df, x="discount_jitter", y="quantity_jitter", hue="membership",
                palette={"Prime": MAIN, "Free": HIGHLIGHT}, alpha=0.4, s=15)
plt.title("Bigger discounts come with slightly bigger quantities")
plt.xlabel("Discount (0.10 = 10%)")
plt.ylabel("Quantity (jittered)")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_scatter.png")
print("Correlation discount vs quantity:", round(df["discount"].corr(df["quantity"]), 2))

print("\n== 6. Correlation heatmap - which numbers move together? ==")
num_cols = ["quantity", "unit_price", "discount", "delivery_days", "rating", "age", "revenue", "profit"]
corr = df[num_cols].corr().round(2)
fig = plt.figure(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, square=True)
plt.title("Slow delivery goes with lower ratings (−0.33)")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_heatmap.png")
print("delivery_days vs rating:", corr.loc["delivery_days", "rating"])
print("discount vs quantity   :", corr.loc["discount", "quantity"])
print("unit_price vs revenue  :", corr.loc["unit_price", "revenue"])
# Remember (Module 3): correlation is not causation. A hint to test faster delivery, not proof.

print("\n== Your turn: delivery_days by city ==")
fig = plt.figure(figsize=(10, 4))
city_order = df.groupby("city")["delivery_days"].median().sort_values().index
sns.boxplot(data=df, x="city", y="delivery_days", order=city_order, color=MAIN)
plt.title("Jaipur, Lucknow and Pune wait longest for delivery")
plt.xticks(rotation=45)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_sns_delivery_by_city.png")
print(df.groupby("city")["delivery_days"].mean().round(2).sort_values(ascending=False).head(3))
