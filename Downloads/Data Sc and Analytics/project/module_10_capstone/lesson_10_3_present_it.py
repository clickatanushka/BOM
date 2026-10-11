"""Video 10.3 - Present it: the 5-slide story (every number comes from the analysis, nothing typed by hand)
Run: python module_10_capstone/lesson_10_3_present_it.py"""

import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from module_08_visualization.charts import (CAPSTONE_GREY, CAPSTONE_HIGHLIGHT, CAPSTONE_INK, CAPSTONE_TEAL,
                                            return_rate_bar, show)
from module_10_capstone import capstone
from module_10_capstone.capstone import lakh
from project_paths import module_output


def new_slide(number, title, subtitle=""):
    fig = plt.figure(figsize=(13.33, 7.5))       # 16:9, like a PowerPoint slide
    fig.text(0.05, 0.90, title, fontsize=22, weight="bold", color=CAPSTONE_INK)
    if subtitle:
        fig.text(0.05, 0.85, subtitle, fontsize=13, color="#555555")
    fig.text(0.95, 0.03, f"ShopKart returns | {number}/5", fontsize=9, color="#888888", ha="right")
    return fig


r = capstone.analyse(show_charts=False)
m, t, model = r["money"], r["tables"], r["model"]
overall = r["overall_rate"]

# Slide 1 - the headline number
slide_1 = new_slide(1, f"{overall:.1%} of orders come back – {lakh(m['revenue_lost'])} of revenue returned in 2025",
                    "The brief: \"Returns are eating our profit. What's going on, and can we predict them?\"")
numbers = [(f"{overall:.1%}", "of 5,000 orders returned"),
           (lakh(m["revenue_lost"]), f"revenue of returned orders ({m['share_of_revenue']:.1%})"),
           (lakh(m["profit_lost"]), "profit those orders would have made")]
for i, (big, small) in enumerate(numbers):
    x = 0.08 + i * 0.31
    slide_1.text(x, 0.50, big, fontsize=44, weight="bold", color=CAPSTONE_HIGHLIGHT if i == 0 else CAPSTONE_INK)
    slide_1.text(x, 0.42, small, fontsize=13, color="#555555")
slide_1.text(0.05, 0.15, "Assumption: a returned order is refunded in full; return shipping and resale are ignored.",
             fontsize=11, style="italic", color="#666666")

# Slide 2 - the biggest leak
pune = t["city"].loc["Pune", "return_rate"]
slide_2 = new_slide(2, f"Pune returns {pune}% of orders – {pune / (overall * 100):.1f}x the average",
                    f"Pune loses {lakh(m['lost_by_city']['Pune'], 2)} "
                    f"({m['pune_share']:.0%} of all returned revenue). Every category is worse there.")
return_rate_bar(t["city"], "Return rate by city", overall, highlight="Pune",
                ax=slide_2.add_axes([0.10, 0.10, 0.48, 0.68]))
pune_vs = t["pune_vs_others"]
ax = slide_2.add_axes([0.66, 0.10, 0.30, 0.68])
y = range(len(pune_vs))
ax.barh([i + 0.2 for i in y], pune_vs["Pune"], height=0.4, color=CAPSTONE_HIGHLIGHT, label="Pune")
ax.barh([i - 0.2 for i in y], pune_vs["Other cities"], height=0.4, color=CAPSTONE_GREY, label="Other cities")
ax.set_yticks(list(y), pune_vs.index)
ax.set_title("Pune vs other cities, by category (%)", loc="left", fontsize=13)
ax.legend(frameon=False, fontsize=9)
ax.spines[["top", "right"]].set_visible(False)

# Slide 3 - the drivers
band, pay = t["delivery_band"], t["payment_mode"]
slide_3 = new_slide(3, "Slow deliveries and cash on delivery bring more returns",
                    f"8+ day deliveries come back {band.loc['8+ days', 'return_rate']}% of the time; "
                    f"COD {pay.loc['COD', 'return_rate']}% vs UPI {pay.loc['UPI', 'return_rate']}%. "
                    "(Slow delivery alone does not explain Pune: Lucknow and Jaipur are as slow.)")
return_rate_bar(band, "By delivery time", overall, highlight="8+ days", sort=False,
                ax=slide_3.add_axes([0.07, 0.10, 0.40, 0.66]))
return_rate_bar(pay, "By payment mode", overall, highlight="COD", ax=slide_3.add_axes([0.58, 0.10, 0.38, 0.66]))

# Slide 4 - the model
logreg, flags = model["results"]["Logistic regression"], model["flagging"]
slide_4 = new_slide(4, f"A simple model catches {logreg['recall']:.0%} of returns before they ship",
                    f"Orders it flags come back {flags['return_rate_flagged']:.1%} of the time vs "
                    f"{flags['return_rate_not_flagged']:.1%} for the rest – about "
                    f"{flags['return_rate_flagged'] / flags['return_rate_not_flagged']:.1f}x as risky.")
ax = slide_4.add_axes([0.07, 0.12, 0.40, 0.62])
rates = [flags["return_rate_flagged"] * 100, flags["return_rate_not_flagged"] * 100]
ax.bar(["Flagged by model", "Not flagged"], rates, color=[CAPSTONE_HIGHLIGHT, CAPSTONE_GREY], width=0.55)
for i, v in enumerate(rates):
    ax.text(i, v + 0.4, f"{v:.1f}%", ha="center", fontsize=12)
ax.set_title("Actual return rate in the test set", loc="left", fontsize=13)
ax.spines[["top", "right"]].set_visible(False)
top = model["importance"].head(6)[::-1]
ax = slide_4.add_axes([0.62, 0.12, 0.34, 0.62])
ax.barh(top.index, top.values, color=CAPSTONE_TEAL)
ax.set_title("What the decision tree relies on most", loc="left", fontsize=13)
ax.spines[["top", "right"]].set_visible(False)
note = (f"Logistic regression, 1,000 test orders: recall {logreg['recall']:.3f}, precision "
        f"{logreg['precision']:.3f}. Rating is not used (it is given after delivery – leakage). "
        f"A 'never returned' guess is {model['baseline_accuracy']:.1%} accurate but catches none.")
slide_4.text(0.07, 0.035, textwrap.fill(note, 150), fontsize=9, color="#666666")

# Slide 5 - the actions
slide_5 = new_slide(5, "Four actions for this month", "Each with an owner, and the finding behind it")
owners = ["Operations", "Product + Payments", "Category team", "Customer support"]
y = 0.76                                             # top of the first action; moves down as we write
for i, ((insight, action), owner) in enumerate(zip(capstone.step_7_insights(r), owners)):
    heading = textwrap.fill(f"{i + 1}. {action}", 105)
    detail = textwrap.fill(f"Owner: {owner}.  Why: {insight}", 160)
    slide_5.text(0.06, y, heading, fontsize=14, weight="bold", color=CAPSTONE_INK, va="top")
    y -= 0.045 * (heading.count("\n") + 1)
    slide_5.text(0.08, y, detail, fontsize=10, color="#555555", va="top")
    y -= 0.028 * (detail.count("\n") + 1) + 0.07

folder = module_output("module_10")
pdf_path = folder / "ShopKart_Returns_Story.pdf"
print("\n== Building the 5-slide deck ==")
with PdfPages(pdf_path) as pdf:
    for number, fig in enumerate([slide_1, slide_2, slide_3, slide_4, slide_5], start=1):
        pdf.savefig(fig)
        fig.savefig(folder / f"slide_{number}.png", dpi=110)
        print(f"Slide {number}: {fig.texts[0].get_text()}")
        show(fig)
print("Saved", pdf_path)
