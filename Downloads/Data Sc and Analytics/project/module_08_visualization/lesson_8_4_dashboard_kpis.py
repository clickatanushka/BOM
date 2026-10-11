"""Video 8.4 - Power BI dashboard
Run: python module_08_visualization/lesson_8_4_dashboard_kpis.py"""

import shutil

import matplotlib.pyplot as plt
import pandas as pd

from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import HIGHLIGHT, MAIN, show
from project_paths import CLEAN_CSV, module_output

OUT = module_output("module_08")


def kpis(d):
    """The five KPI cards, like the five DAX measures in the build guide."""
    return pd.Series({
        "Total Revenue (₹)": round(d["revenue"].sum(), 2),
        "Total Orders": len(d),
        "Return Rate %": round(d["returned"].eq("Y").mean() * 100, 2),
        "Avg Rating": round(d["rating"].mean(), 2),       # blanks are ignored, like AVERAGE in Power BI
        "Total Profit (₹)": round(d["profit"].sum(), 2),
    })


def lakh(x):
    return f"₹{x/100000:,.1f} L"


df = load_clean()

print("\n== 0. The file Power BI loads ==")
# Power BI: Get data -> Text/CSV. The table name must stay shopkart_clean - the DAX measures use it.
path = OUT / "shopkart_clean.csv"
shutil.copyfile(CLEAN_CSV, path)
print(f"Saved {path.name} {df.shape} -> load this file in Power BI")

print("\n== 1. The five KPIs (no slicer selected) ==")
k = kpis(df)
print(k.to_string())

print("\n== 2. KPIs when a slicer is selected ==")
# Click these slicer values in Power BI and compare (Section 10 of the build guide).
checks = {
    "All data": df,
    "City = Pune": df[df["city"] == "Pune"],
    "City = Delhi": df[df["city"] == "Delhi"],
    "City = Mumbai": df[df["city"] == "Mumbai"],
    "City = Bengaluru": df[df["city"] == "Bengaluru"],
    "Membership = Prime": df[df["membership"] == "Prime"],
    "Membership = Free": df[df["membership"] == "Free"],
    "Pune + Prime": df[(df["city"] == "Pune") & (df["membership"] == "Prime")],
    "Pune + Fashion (practice)": df[(df["city"] == "Pune") & (df["category"] == "Fashion")],
}
table = pd.DataFrame({name: kpis(d) for name, d in checks.items()}).T
table["Total Orders"] = table["Total Orders"].astype(int)
with pd.option_context("display.width", 140, "display.max_columns", 10):
    print(table)
path = OUT / "M08_dashboard_expected_kpis.csv"
table.to_csv(path, index_label="selection")
print(f"Saved {path.name}")

print("\n== 3. Numbers behind each visual ==")
print(df.groupby("category")["revenue"].sum().sort_values(ascending=False).round(2), "\n")
print(df.groupby("order_month")["revenue"].sum().round(2), "\n")
print(df.groupby("city")["revenue"].sum().sort_values(ascending=False).round(2))

print("\n== 4. Draw the reference mock-up ==")
# Slicers on the left, 5 KPI cards on top, three charts below.
cat = df.groupby("category")["revenue"].sum().sort_values() / 100000
month = df.groupby("order_month")["revenue"].sum() / 100000
city = df.groupby("city")["revenue"].sum().sort_values() / 100000

fig = plt.figure(figsize=(16, 9), facecolor="#f3f2ef")
fig.text(0.02, 0.95, "ShopKart Sales Dashboard – 2025", fontsize=20, weight="bold")
fig.text(0.02, 0.92, "Source: shopkart_clean.csv (5,000 orders)", fontsize=10, color="#52514e")

# Slicer panel (left)
sl = fig.add_axes([0.02, 0.06, 0.13, 0.82])
sl.set_xticks([])
sl.set_yticks([])
sl.set_facecolor("white")
sl.text(0.08, 0.96, "City", weight="bold", fontsize=12, va="top")
for i, c in enumerate(sorted(df["city"].unique())):
    sl.text(0.08, 0.91 - i * 0.045, "☐  " + c, fontsize=10, va="top")
sl.text(0.08, 0.40, "Membership", weight="bold", fontsize=12, va="top")
for i, m in enumerate(["Free", "Prime"]):
    sl.text(0.08, 0.35 - i * 0.045, "☐  " + m, fontsize=10, va="top")
sl.text(0.08, 0.20, "Category", weight="bold", fontsize=12, va="top")
sl.text(0.08, 0.15, "(optional 3rd slicer)", fontsize=9, color="#52514e", va="top")

# KPI cards (top row)
cards = [("Total Revenue", lakh(k["Total Revenue (₹)"])),
         ("Total Orders", f"{int(k['Total Orders']):,}"),
         ("Return Rate %", f"{k['Return Rate %']:.1f}%"),
         ("Avg Rating", f"{k['Avg Rating']:.2f}"),
         ("Total Profit", lakh(k["Total Profit (₹)"]))]
for i, (label, value) in enumerate(cards):
    ax = fig.add_axes([0.17 + i * 0.165, 0.73, 0.15, 0.15])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("white")
    ax.text(0.5, 0.58, value, ha="center", va="center", fontsize=24, weight="bold",
            color=HIGHLIGHT if label == "Return Rate %" else "#0b0b0b")
    ax.text(0.5, 0.2, label, ha="center", fontsize=11, color="#52514e")

ax1 = fig.add_axes([0.21, 0.08, 0.2, 0.55])
ax1.barh(cat.index, cat.values, color=MAIN)
ax1.set_title("Revenue by Category (₹ L)", loc="left")
for i, v in enumerate(cat.values):
    ax1.text(v + 1, i, f"{v:.0f}", va="center", fontsize=9)
ax1.set_xlim(0, cat.max() * 1.2)

ax2 = fig.add_axes([0.46, 0.08, 0.27, 0.55])
ax2.plot(month.index, month.values, marker="o", color=MAIN, linewidth=2)
ax2.set_xticks(month.index, ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"])
ax2.set_ylim(0, month.max() * 1.2)
ax2.set_title("Revenue by Month (₹ L)", loc="left")

ax3 = fig.add_axes([0.81, 0.08, 0.17, 0.55])
ax3.barh(city.index, city.values, color=MAIN)
ax3.set_title("Revenue by City (₹ L)", loc="left")
ax3.set_xlim(0, city.max() * 1.25)

for a in (ax1, ax2, ax3):
    a.spines[["top", "right"]].set_visible(False)

# Whole figure, page colour kept (no bbox crop: the layout is placed by hand)
path = OUT / "M08_dashboard_mockup.png"
fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
show()
print(f"Saved {path.name}")
