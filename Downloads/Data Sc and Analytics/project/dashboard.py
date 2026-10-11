"""ShopKart Returns Dashboard - the finished course project: messy data -> clean -> explore -> predict -> act.
Built from the modules' own code: cleaning (6), charts (8), model (9), capstone findings (10).
Run: .venv/bin/streamlit run dashboard.py"""

import contextlib
import io

import altair as alt
import pandas as pd
import streamlit as st

from module_06_pandas_eda.cleaning import build_clean_table, clean_orders, final_checks, load_clean, load_raw
from module_08_visualization.charts import CAPSTONE_GREY, CAPSTONE_HIGHLIGHT, MAIN, MONTH_NAMES, return_table
from module_09_machine_learning.models import (RETURN_FEATURES, evaluate_classifier, flagging_summary,
                                               return_features, return_models, split)
from module_10_capstone import capstone
from project_paths import module_output

st.set_page_config(page_title="ShopKart Returns Dashboard", page_icon="🛒", layout="wide")
INK = "#FAFAFA" if st.context.theme.type == "dark" else "#1B2433"     # chart text that works in both themes
MIN_ORDERS = 50                                                     # below this a return rate is too noisy


def inr(value):
    """₹ with Indian digit grouping: 14704649.7 -> ₹1,47,04,650."""
    digits = f"{round(value):d}"
    head, tail = digits[:-3], digits[-3:]
    while len(head) > 2:
        head, tail = head[:-2], head[-2:] + "," + tail
    return "₹" + (head + "," + tail if head else tail)


@st.cache_data
def orders():
    df = load_clean()                                                   # Module 6
    df["month"] = pd.Categorical(df["order_date"].dt.month.map(lambda m: MONTH_NAMES[m - 1]), MONTH_NAMES,
                                 ordered=True)
    df["delivery"] = pd.cut(df["delivery_days"], bins=[0, 3, 4, 5, 7, 30],
                            labels=["2-3 days", "4 days", "5 days", "6-7 days", "8+ days"])
    return df


@st.cache_data
def cleaning_examples():
    """One real raw row per kind of mess, next to what Module 6's clean_orders() made of it."""
    raw, customers, products = load_raw()
    unique = raw.drop_duplicates()
    clean = clean_orders(raw)                          # keeps the raw row index, so rows line up
    city = unique["city"].astype(str)
    dates = unique["order_date"].astype(str).str.match(r"^\d{2}-")
    prices = unique["unit_price"].astype(str)
    payment = unique["payment_mode"]
    # (problem, column, every row with the problem, the rows to pick a clear example from)
    problems = [
        ("Date in two formats", "order_date", dates, dates),
        ("Price typed as text", "unit_price", prices.str.contains("₹|,"), prices.str.contains(",")),
        ("27 spellings of 10 cities", "city", city != clean["city"], (city != clean["city"]) & (city == city.str.strip())),
        ("Payment mode 'upi' or blank", "payment_mode", payment.isna() | (payment == "upi"), payment.isna()),
        ("Blank discount", "discount", unique["discount"].isna(), unique["discount"].isna()),
        ("'Yes'/'No' mixed with 'Y'/'N'", "returned", unique["returned"].isin(["Yes", "No"]),
         unique["returned"].isin(["Yes", "No"])),
        ("Quantity 99 (a typo)", "quantity", unique["quantity"] == 99, unique["quantity"] == 99),
    ]
    rows = []
    for problem, column, affected, example in problems:
        i = unique.index[example][0]
        before, after = unique.loc[i, column], clean.loc[i, column]
        rows.append({"Problem": problem, "Rows affected": int(affected.sum()),
                     "Before": "(blank)" if pd.isna(before) else str(before),
                     "After": after.strftime("%Y-%m-%d") if column == "order_date" else str(after)})
    checks = final_checks(build_clean_table(raw, customers, products))
    return pd.DataFrame(rows), len(raw), len(unique), raw["city"].nunique(), checks


@st.cache_resource
def return_model():
    """Module 9 / capstone settings: logistic regression on order-time facts only."""
    X, y = return_features(orders())
    X_train, X_test, y_train, y_test = split(X, y)
    model = return_models()["Logistic regression"].fit(X_train, y_train)
    return model, list(X.columns), evaluate_classifier(model, X_test, y_test), flagging_summary(model, X_test, y_test)


@st.cache_resource
def findings():
    with contextlib.redirect_stdout(io.StringIO()):                   # the capstone prints as it goes
        results = capstone.analyse(show_charts=False)                 # Module 10
    return capstone.step_7_insights(results), results["money"]


def rate_bars(table, label, overall, keep_order=False):
    """Return-rate bars, worst one highlighted, value labels and a dashed line at the average (Module 8 style)."""
    data = table.reset_index()
    data[label] = data[label].astype(str)
    worst = data.loc[data["return_rate"].idxmax(), label]
    order = data[label].tolist() if keep_order else "-x"
    bars = alt.Chart(data).mark_bar().encode(
        x=alt.X("return_rate:Q", title="Return rate (%)"),
        y=alt.Y(f"{label}:N", sort=order, title=None, axis=alt.Axis(labelLimit=200)),
        color=alt.condition(alt.datum[label] == worst, alt.value(CAPSTONE_HIGHLIGHT), alt.value(CAPSTONE_GREY)),
        tooltip=[label, "orders", "returns", "return_rate"])
    text = bars.mark_text(align="left", dx=4).encode(text=alt.Text("return_rate:Q", format=".1f"),
                                                     color=alt.value(INK))
    rule = alt.Chart(pd.DataFrame({"x": [overall]})).mark_rule(strokeDash=[4, 4], color=INK).encode(x="x:Q")
    return (bars + text + rule).properties(height=max(140, 34 * len(data)))


df_all = orders()
overall = (df_all["returned"] == "Y").mean() * 100

# ---------------- header + filters ----------------
st.title("🛒 ShopKart Returns Dashboard")
st.markdown("**The brief:** *\"Returns are eating our profit. What's going on, and can we predict them?\"*  \n"
            "5,000 orders from 2025, 10 cities, 5 categories - cleaned, charted and modelled in this course.")

with st.sidebar:
    st.header("Filters")
    st.caption("Apply to the Explore tab")
    pick = {col: st.multiselect(col.replace("_", " ").title(), sorted(df_all[col].unique()))
            for col in ["city", "category", "payment_mode", "membership"]}
    first, last = st.select_slider("Months", MONTH_NAMES, value=("Jan", "Dec"))

df = df_all[df_all["month"].between(first, last)]
for col, chosen in pick.items():
    if chosen:
        df = df[df[col].isin(chosen)]

clean_tab, explore_tab, predict_tab, findings_tab = st.tabs(
    ["🧹 Before & after cleaning", "📊 Explore", "🔮 Return risk predictor", "💡 Findings"])

# ---------------- 1. Before & after cleaning ----------------
with clean_tab:
    st.caption("Module 2 (Excel) + Module 6 (pandas): the messy raw file, and what cleaning.py does to it")
    examples, raw_rows, unique_rows, raw_cities, checks = cleaning_examples()
    k = st.columns(4)
    k[0].metric("Orders", f"{unique_rows:,}", f"{unique_rows - raw_rows} duplicates (from {raw_rows:,})",
                delta_color="off")
    k[1].metric("Cities", df_all["city"].nunique(), f"{df_all['city'].nunique() - raw_cities} spellings (from {raw_cities})",
                delta_color="off")
    k[2].metric("Rows fixed", f"{examples['Rows affected'].sum() + raw_rows - unique_rows:,}")
    k[3].metric("Quality checks", f"{sum(checks.values())} / {len(checks)} passed")
    st.subheader("What was wrong, and the fix")
    st.dataframe(examples, hide_index=True, width="stretch")
    st.caption("A real row for each problem in orders_raw.csv, before and after cleaning. "
               "Blank ratings are kept on purpose: 'not rated' is real information.")

# ---------------- 2. Explore ----------------
with explore_tab:
    st.caption("Module 6 (pandas) + Module 8 (charts) - use the filters on the left")
    returned = df["returned"] == "Y"
    rate = returned.mean() * 100 if len(df) else 0
    k = st.columns(5)
    k[0].metric("Revenue", inr(df["revenue"].sum()))
    k[1].metric("Orders", f"{len(df):,}")
    k[2].metric("Return rate", f"{rate:.1f}%", f"{rate - overall:+.1f} pts vs all orders" if len(df) < len(df_all)
                else None, delta_color="inverse")
    k[3].metric("Revenue of returned orders", inr(df.loc[returned, "revenue"].sum()))
    k[4].metric("Avg rating", f"{df['rating'].mean():.2f} ★" if len(df) else "-")

    if len(df) < MIN_ORDERS:
        st.info(f"Only {len(df)} orders match these filters - too few for reliable charts. Widen the filters.")
    else:
        left, right = st.columns(2, gap="large")
        with left:
            st.subheader("Where do returns happen?")
            dims = {"City": "city", "Category": "category", "Payment mode": "payment_mode", "Delivery time": "delivery"}
            by = dims[st.radio("Return rate by", list(dims), horizontal=True, label_visibility="collapsed")]
            st.altair_chart(rate_bars(return_table(df, by), by, rate, keep_order=by == "delivery"),   # Module 8
                            width="stretch")
            st.caption(f"Dashed line = average of the selected orders ({rate:.1f}%).")
        with right:
            st.subheader("Revenue by month")
            monthly = df.groupby("month", observed=True)["revenue"].sum().reset_index()
            st.altair_chart(alt.Chart(monthly).mark_area(line=True, opacity=0.25, color=MAIN).encode(
                x=alt.X("month:N", sort=MONTH_NAMES, title=None), y=alt.Y("revenue:Q", title="Revenue (₹)"),
                tooltip=["month", alt.Tooltip("revenue:Q", format=",.0f")]).properties(height=340), width="stretch")

# ---------------- 3. Return risk predictor ----------------
with predict_tab:
    st.caption("Module 9 (machine learning) - logistic regression trained only on what is known when the order "
               "is placed (no rating: that would be leakage)")
    model, columns, scores, flags = return_model()
    m = st.columns(4)
    m[0].metric("Catches (recall)", f"{scores['recall']:.0%}", help="Share of real returns the model flags")
    m[1].metric("Precision", f"{scores['precision']:.0%}", help="Share of flagged orders that really came back")
    m[2].metric("Flagged orders come back", f"{flags['return_rate_flagged']:.1%}")
    m[3].metric("Not-flagged orders come back", f"{flags['return_rate_not_flagged']:.1%}")

    st.subheader("Score a new order")
    with st.form("order"):
        c = st.columns(3)
        order = {
            "category": c[0].selectbox("Category", sorted(df_all["category"].unique())),
            "city": c[1].selectbox("City", sorted(df_all["city"].unique()), index=3),
            "payment_mode": c[2].selectbox("Payment mode", sorted(df_all["payment_mode"].unique())),
            "delivery_days": c[0].slider("Promised delivery (days)", 1, 12, 4),
            "discount": c[1].select_slider("Discount", [float(d) for d in sorted(df_all["discount"].unique())],
                                           value=0.1, format_func=lambda d: f"{d:.0%}"),
            "membership": c[2].radio("Membership", ["Free", "Prime"], horizontal=True),
        }
        submitted = st.form_submit_button("Predict return risk", type="primary")
    if submitted:
        row = pd.get_dummies(pd.DataFrame([order])[RETURN_FEATURES], dtype=int).reindex(columns=columns, fill_value=0)
        risk = model.predict_proba(row)[0, 1]
        a, b = st.columns([1, 2])
        a.metric("Model risk score", f"{risk:.0%}")
        a.progress(float(risk))
        if model.predict(row)[0] == 1:
            b.error("🚩 **Flag this order** - send a confirmation call / size-check message before shipping.")
        else:
            b.success("✅ **Low risk** - ship as normal.")
        b.caption(f"Overall {overall:.1f}% of orders are returned. Above 50% the model flags the order; it is trained "
                  "to take the rare returns seriously, so scores run higher than the real rate.")

# ---------------- 4. Findings ----------------
with findings_tab:
    st.caption("Module 10 (capstone) - every number below is computed, nothing typed by hand")
    insights, money = findings()
    for number, (insight, action) in enumerate(insights, start=1):
        with st.container(border=True):
            st.markdown(f"**{number}. {insight}**")
            st.markdown(f"→ {action}")
    st.caption(f"Revenue of returned orders: {capstone.lakh(money['revenue_lost'])} "
               f"({money['share_of_revenue']:.1%} of revenue). Assumption: full refund, no resale.")

    deck = module_output("module_10")
    slides = sorted(deck.glob("slide_*.png"))
    if slides:
        st.subheader("The 5-slide deck")
        slide = st.select_slider("Slide", options=slides, format_func=lambda p: p.stem.replace("_", " ").title())
        st.image(str(slide), width="stretch")
        pdf = deck / "ShopKart_Returns_Story.pdf"
        st.download_button("Download the deck (PDF)", pdf.read_bytes(), file_name=pdf.name, mime="application/pdf")
    else:
        st.caption("Run `python module_10_capstone/lesson_10_3_present_it.py` to build the 5-slide deck.")
