"""Video 8.5 - Data storytelling
Run: python module_08_visualization/lesson_8_5_story_charts.py"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import GREY, HIGHLIGHT, return_table, save_and_show

MODULE = "module_08"

df = load_clean()
df["is_returned"] = (df["returned"] == "Y").astype(int)   # 1 = returned, 0 = kept

print("\n== Finding 1 - Pune's return rate ==")
overall = df["is_returned"].mean() * 100
by_city = (df.groupby("city")["is_returned"].mean() * 100).sort_values(ascending=False)
ratio = by_city["Pune"] / overall
pune = df[df["city"] == "Pune"]
print(f"Overall return rate : {overall:.1f}%")
print(f"Pune return rate    : {by_city['Pune']:.1f}%  ({pune['is_returned'].sum()} of {len(pune)} orders)")
print(f"Ratio               : {ratio:.2f}x")
print(f"Next highest city   : {by_city.index[1]} {by_city.iloc[1]:.1f}%")
print(f"Revenue of returned Pune orders: ₹{pune.loc[pune['is_returned'] == 1, 'revenue'].sum():,.0f}")
# The same numbers as one table (charts.return_table, reused in the Module 10 capstone)
print(return_table(df, "city").sort_values("return_rate", ascending=False).head(3))

fig, ax = plt.subplots(figsize=(9, 4.5))
s = by_city.sort_values()
ax.barh(s.index, s.values, color=[HIGHLIGHT if c == "Pune" else GREY for c in s.index])
ax.axvline(overall, color="black", linestyle="--", linewidth=1)
ax.text(overall + 0.3, -0.6, f"average {overall:.1f}%", fontsize=9)
for i, v in enumerate(s.values):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)
ax.set_title(f"Pune returns are {ratio:.1f}x the average", loc="left", fontsize=14, weight="bold")
ax.set_xlabel("Return rate (%)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_story1_pune_returns.png")

print("\n== Finding 2 - Is it just slow delivery? ==")
# Pune deliveries are slower. But even at the SAME delivery speed, Pune returns more.
df["delivery_band"] = pd.cut(df["delivery_days"], bins=[0, 4, 5, 7, 20],
                             labels=["2-4 days", "5 days", "6-7 days", "8+ days"])
df["area"] = df["city"].where(df["city"] == "Pune", "Other cities")
band = (df.pivot_table(index="delivery_band", columns="area", values="is_returned",
                       aggfunc="mean", observed=True) * 100).round(1)
print(band)
print()
print("Average delivery days:")
print(df.groupby("area")["delivery_days"].mean().round(2))

fig, ax = plt.subplots(figsize=(9, 4.5))
x = np.arange(len(band))
for area, shift, color in [("Other cities", -0.2, GREY), ("Pune", 0.2, HIGHLIGHT)]:
    ax.bar(x + shift, band[area], width=0.4, color=color, label=area)
    for i, v in enumerate(band[area]):
        ax.text(i + shift, v + 0.8, f"{v:.0f}%", ha="center", fontsize=9)
ax.set_xticks(x, band.index)
ax.set_ylabel("Return rate (%)")
ax.set_title("Pune returns more at every delivery speed", loc="left", fontsize=14, weight="bold")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_story2_pune_by_delivery.png")

print("\n== Finding 3 - Which category to look at first? ==")
cat = df.groupby("category")["is_returned"].mean() * 100
pune_cat = pune["returned"].eq("Y").groupby(pune["category"]).mean() * 100
print("All cities:")
print(cat.round(1).sort_values(ascending=False))
print("\nPune only:")
print(pune_cat.round(1).sort_values(ascending=False))

fig, ax = plt.subplots(figsize=(9, 4.5))
s = cat.sort_values()
ax.barh(s.index, s.values, color=[HIGHLIGHT if c == "Fashion" else GREY for c in s.index])
for i, v in enumerate(s.values):
    ax.text(v + 0.3, i, f"{v:.1f}%", va="center", fontsize=9)
ax.set_title("Fashion has the highest return rate of any category", loc="left", fontsize=14, weight="bold")
ax.set_xlabel("Return rate (%)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_story3_fashion_returns.png")
