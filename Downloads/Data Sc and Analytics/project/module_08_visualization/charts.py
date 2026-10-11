"""
Module 8 - the course colours and chart helpers that later modules reuse.
Reused by Module 10 (capstone.py, lesson_10_3_present_it.py): show, save_and_show, return_table,
return_rate_bar and the CAPSTONE_* colours.
"""

import matplotlib.pyplot as plt

from project_paths import module_output

MAIN = "#2a78d6"        # blue   - normal bars and lines
HIGHLIGHT = "#eb6834"   # orange - the one thing we want people to notice
GREY = "#b8b6ae"        # grey   - everything else
RETURN_COLORS = {"N": MAIN, "Y": HIGHLIGHT}   # same colour = same meaning in every chart

# Capstone colours (Module 10 findings deck)
CAPSTONE_HIGHLIGHT = "#E76F51"
CAPSTONE_GREY = "#9AA8BC"
CAPSTONE_INK = "#1B2433"
CAPSTONE_TEAL = "#2A9D8F"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def show(fig=None):
    """plt.show(), skipped with MPLBACKEND=Agg (no window; matplotlib 3.11 warns), then close the figure."""
    if plt.get_backend().lower() != "agg":
        plt.show()
    plt.close(fig if fig is not None else "all")


def save_and_show(fig, module, name):
    """Save fig as outputs/<module>/<name> (PNG, dpi 150), then show it. Returns the path."""
    path = module_output(module) / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    show(fig)
    return path


def return_table(df, column):
    """Orders, returns and return rate (%) for each value of a column."""
    t = (df.assign(_returned=df["returned"].eq("Y").astype(int))
         .groupby(column, observed=True)
         .agg(orders=("_returned", "size"), returns=("_returned", "sum"), return_rate=("_returned", "mean")))
    t["return_rate"] = (t["return_rate"] * 100).round(1)
    return t


def return_rate_bar(table, title, overall_rate, highlight=None, sort=True, ax=None):
    """
    Horizontal return-rate bars (a return_table()) with a dashed line at overall_rate (a fraction, e.g. 0.137).
    sort=True puts the smallest rate at the bottom; False keeps the table order top to bottom.
    Pass ax to draw into someone else's layout (e.g. a slide) - then the figure is left alone.
    """
    t = table.sort_values("return_rate") if sort else table.iloc[::-1]
    own_figure = ax is None
    if own_figure:
        _, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(t.index.astype(str), t["return_rate"],
            color=[CAPSTONE_HIGHLIGHT if name == highlight else CAPSTONE_GREY for name in t.index])
    ax.axvline(overall_rate * 100, color=CAPSTONE_INK, linestyle="--", linewidth=1)
    ax.text(overall_rate * 100 + 0.3, -0.6, f"Overall {overall_rate:.1%}", fontsize=9)
    for i, v in enumerate(t["return_rate"]):
        ax.text(v + 0.3, i, f"{v}%", va="center", fontsize=9)
    ax.set_title(title, loc="left", fontsize=13)
    ax.set_xlabel("Return rate (%)")
    ax.spines[["top", "right"]].set_visible(False)
    if own_figure:
        ax.figure.tight_layout()
    return ax.figure
