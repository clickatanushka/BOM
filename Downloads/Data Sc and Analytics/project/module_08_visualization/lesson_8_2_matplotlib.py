"""Video 8.2 - Matplotlib
Run: python module_08_visualization/lesson_8_2_matplotlib.py"""

import matplotlib.pyplot as plt

from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import HIGHLIGHT, MAIN, MONTH_NAMES, show
from project_paths import module_output

OUT = module_output("module_08")      # outputs/module_08/ - every chart is saved here

print("\n== Step 1 - Load the data ==")
df = load_clean()                 # the clean file from the end of Module 6
print(df.shape)
print(df.head(3))

print("\n== Step 2 - Bar chart: revenue by category ==")
cat_rev = df.groupby("category")["revenue"].sum().sort_values(ascending=False) / 100000   # in lakh rupees
print(cat_rev.round(1))

plt.bar(cat_rev.index, cat_rev.values)
plt.savefig(OUT / "M08_first_bar_chart.png", dpi=150, bbox_inches="tight")
show()       # plt.show(), skipped when there is no window (tests)

# That works, but a chart without a title and axis labels is unfinished.
plt.figure(figsize=(8, 4))                   # width 8, height 4 (inches)
plt.bar(cat_rev.index, cat_rev.values, color=MAIN)
plt.title("Electronics brings half of ShopKart's revenue")   # a title that says the finding
plt.xlabel("Category")
plt.ylabel("Revenue (₹ lakh)")
plt.tight_layout()                            # stops labels being cut off
plt.savefig(OUT / "M08_revenue_by_category.png", dpi=150, bbox_inches="tight")  # save BEFORE plt.show()
show()

print("\n== Step 3 - Line chart: monthly revenue ==")
monthly = df.groupby("order_month")["revenue"].sum() / 100000   # order_month: 1 = January
print(monthly.round(1))

plt.figure(figsize=(9, 4))
plt.plot(monthly.index, monthly.values, marker="o", color=MAIN, linewidth=2)
plt.xticks(monthly.index, MONTH_NAMES)
plt.ylim(0, monthly.max() * 1.15)             # start the y-axis at 0
plt.title("Revenue peaks in Oct–Nov (festive season)")
plt.xlabel("Month (2025)")
plt.ylabel("Revenue (₹ lakh)")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(OUT / "M08_monthly_revenue.png", dpi=150, bbox_inches="tight")
show()
print("Best month :", MONTH_NAMES[monthly.idxmax() - 1], round(monthly.max(), 1), "lakh")
print("Worst month:", MONTH_NAMES[monthly.idxmin() - 1], round(monthly.min(), 1), "lakh")

print("\n== Step 4 - Histogram: how big is a typical order? ==")
# Most orders are small and a few are huge -> right-skewed (Module 3)
plt.figure(figsize=(8, 4))
plt.hist(df["revenue"], bins=50, color=MAIN, edgecolor="white")
plt.title("Order revenue is right-skewed: a few very large orders")
plt.xlabel("Order revenue (₹)")
plt.ylabel("Number of orders")
plt.tight_layout()
plt.savefig(OUT / "M08_revenue_histogram_all.png", dpi=150, bbox_inches="tight")
show()
print("Median order:", df["revenue"].median(), " Mean order:", round(df["revenue"].mean(), 2),
      " Biggest order:", df["revenue"].max())

# Zoom in on orders up to ₹10,000 to see the shape of the "normal" orders
small = df[df["revenue"] <= 10000]
print(len(small), "of", len(df), "orders are ₹10,000 or less")
plt.figure(figsize=(8, 4))
plt.hist(small["revenue"], bins=40, color=MAIN, edgecolor="white")
plt.axvline(df["revenue"].median(), color=HIGHLIGHT, linestyle="--", label="Median")
plt.legend()
plt.title("Most orders are below ₹3,000")
plt.xlabel("Order revenue (₹)")
plt.ylabel("Number of orders")
plt.tight_layout()
plt.savefig(OUT / "M08_revenue_histogram.png", dpi=150, bbox_inches="tight")
show()

print("\n== Step 5 - Two charts side by side (subplots) ==")
# plt.subplots(1, 2) gives one figure with 2 boxes (axes): use ax.set_title instead of plt.title
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].bar(cat_rev.index, cat_rev.values, color=MAIN)
axes[0].set_title("Revenue by category (₹ lakh)")
axes[1].plot(monthly.index, monthly.values, marker="o", color=MAIN)
axes[1].set_xticks(monthly.index, MONTH_NAMES)
axes[1].set_ylim(0, monthly.max() * 1.15)
axes[1].set_title("Revenue by month (₹ lakh)")
plt.tight_layout()
plt.savefig(OUT / "M08_two_charts.png", dpi=150, bbox_inches="tight")
show()
print(sorted(p.name for p in OUT.glob("M08_*.png")))

print("\n== Your turn: horizontal bar chart of revenue by city ==")
city_rev = df.groupby("city")["revenue"].sum().sort_values() / 100000
plt.figure(figsize=(8, 5))
plt.barh(city_rev.index, city_rev.values, color=MAIN)
plt.title("Delhi, Bengaluru and Mumbai lead revenue")
plt.xlabel("Revenue (₹ lakh)")
plt.tight_layout()
plt.savefig(OUT / "M08_revenue_by_city.png", dpi=150, bbox_inches="tight")
show()
