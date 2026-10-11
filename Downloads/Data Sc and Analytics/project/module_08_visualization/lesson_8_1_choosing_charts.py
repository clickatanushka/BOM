"""Video 8.1 - Choosing the right chart
Run: python module_08_visualization/lesson_8_1_choosing_charts.py"""

import matplotlib.pyplot as plt

from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import GREY, HIGHLIGHT, MAIN, save_and_show

MODULE = "module_08"

print("\n== Load the clean ShopKart data (Module 6) ==")
df = load_clean()
print(df.shape)
print(df.head(3))

print("\n== Makeover 1 - the truncated axis ==")
top2 = df.groupby("city")["revenue"].sum().sort_values(ascending=False).head(2) / 100000   # in lakh rupees
print(top2.round(2))
print("Delhi is", round((top2.iloc[0] / top2.iloc[1] - 1) * 100, 1), "% higher than Bengaluru")

# BEFORE: y-axis starts at 22 lakh -> the gap looks huge
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(top2.index, top2.values, color=[HIGHLIGHT, MAIN], width=0.6)
ax.set_ylim(22, 23.4)
ax.set_title("Delhi CRUSHES Bengaluru!")
ax.set_ylabel("Revenue (₹ lakh)")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_makeover1_truncated_BEFORE.png")

# AFTER: y-axis starts at 0 -> honest picture, plus a message title
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(top2.index, top2.values, color=MAIN, width=0.6)
ax.set_ylim(0, 26)
for i, v in enumerate(top2.values):
    ax.text(i, v + 0.4, f"₹{v:.1f} L", ha="center")
ax.set_title("Delhi and Bengaluru are almost tied (3% gap)")
ax.set_ylabel("Revenue (₹ lakh)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_makeover1_truncated_AFTER.png")

print("\n== Makeover 2 - the 3D pie ==")
city_rev = df.groupby("city")["revenue"].sum().sort_values(ascending=False)
share = (city_rev / city_rev.sum() * 100).round(1)
print(share)

# BEFORE: a tilted, exploded, shadowed pie with 10 slices
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.pie(city_rev.values, labels=city_rev.index, shadow=True, explode=[0.08] * len(city_rev), startangle=200,
       colors=plt.cm.tab10.colors)
ax.set_aspect(0.45)          # squash the circle so it looks "3D" - this distorts the slices
ax.set_title("Revenue by City")
plt.tight_layout()
save_and_show(fig, MODULE, "M08_makeover2_3Dpie_BEFORE.png")

# AFTER: sorted horizontal bar chart, one colour, highlight the leader
fig, ax = plt.subplots(figsize=(6, 4.5))
s = share.sort_values()                       # smallest at bottom, biggest on top
ax.barh(s.index, s.values, color=[HIGHLIGHT if c == "Delhi" else MAIN for c in s.index])
for i, v in enumerate(s.values):
    ax.text(v + 0.2, i, f"{v}%", va="center")
ax.set_xlabel("Share of total revenue (%)")
ax.set_title("Delhi brings the most revenue (15.8%)")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_makeover2_3Dpie_AFTER.png")

print("\n== Makeover 3 - clutter vs focus ==")
ret_city = (df["returned"].eq("Y").groupby(df["city"]).mean() * 100).sort_values(ascending=False)
overall = df["returned"].eq("Y").mean() * 100
ratio = ret_city["Pune"] / overall
print(ret_city.round(1))
print("Overall return rate:", round(overall, 1), "%")
print("Pune vs overall:", round(ratio, 1), "x")

# BEFORE: rainbow colours, gridlines, no message
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(ret_city.index, ret_city.values, color=plt.cm.tab10.colors)
ax.grid(True)
ax.set_title("Return Rate by City")
plt.xticks(rotation=45)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_makeover3_clutter_BEFORE.png")

# AFTER: grey bars, Pune highlighted, average line, message title
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(ret_city.index, ret_city.values, color=[HIGHLIGHT if c == "Pune" else GREY for c in ret_city.index])
ax.axhline(overall, color="black", linestyle="--", linewidth=1)
ax.text(9.4, overall + 0.6, f"Average {overall:.1f}%", ha="right")
ax.set_title(f"Pune returns are {ratio:.1f}x the average")
ax.set_ylabel("Return rate (%)")
ax.spines[["top", "right"]].set_visible(False)
plt.xticks(rotation=45)
plt.tight_layout()
save_and_show(fig, MODULE, "M08_makeover3_clutter_AFTER.png")
print("\nAll six images are in outputs/module_08/")
