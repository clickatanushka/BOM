"""
Module 10 - the capstone: "Returns are eating our profit. What's going on, and can we predict them?"

Each step reuses an earlier module (4 SQL, 6 pandas, 8 charts, 9 model). lesson_10_2_build_it.py runs the steps
on camera, lesson_10_3_present_it.py turns analyse() into the deck, and tests/test_project.py checks analyse().
Run: python module_10_capstone/capstone.py
"""

import matplotlib.pyplot as plt
import pandas as pd

from module_04_sql.sql_runner import run_query
from module_06_pandas_eda.cleaning import load_clean
from module_08_visualization.charts import return_rate_bar, return_table, save_and_show
from module_09_machine_learning.models import (baseline_accuracy, evaluate_classifier, flagging_summary,
                                               return_features, return_models, split)
from project_paths import module_output

MODULE = "module_10"

# Q3 of sql/M10_capstone_shopkart.sql: one joined table for Python
CAPSTONE_QUERY = """
SELECT o.order_id, o.order_date, o.customer_id, o.product_id,
       o.quantity, o.unit_price, o.discount, o.city, o.payment_mode,
       o.delivery_days, o.rating, o.returned,
       p.product_name, p.category, p.cost_price,
       c.gender, c.age, c.membership,
       ROUND(o.quantity * o.unit_price * (1 - o.discount), 2) AS revenue
FROM orders AS o
INNER JOIN products AS p ON o.product_id = p.product_id
LEFT JOIN customers AS c ON o.customer_id = c.customer_id
ORDER BY o.order_id;
"""

# The four return-rate charts: (column, title, bar to highlight, sort by rate?)
CHARTS = [
    ("city", "Pune returns 1 in 3 orders – more than double any other city", "Pune", True),
    ("category", "Fashion has the highest return rate", "Fashion", True),
    ("payment_mode", "Cash on Delivery orders are returned more often", "COD", True),
    ("delivery_band", "The slower the delivery, the more returns", "8+ days", False),
]


def step_1_load_with_sql():
    df = run_query(CAPSTONE_QUERY)
    print("Step 1 - loaded with SQL:", df.shape)
    return df


def step_2_check(df):
    print("\nStep 2 - check the data")
    print("Rows, columns:", df.shape)
    print("Duplicate order_ids:", df["order_id"].duplicated().sum())
    missing = df.isnull().sum()
    print("Missing values (only columns with some):", missing[missing > 0].to_dict())
    print("Values in returned:", df["returned"].value_counts().to_dict())

    # The database holds the cleaned orders; Module 6 cleaned the raw CSV in pandas. They must agree.
    clean = load_clean()
    same_orders = set(df["order_id"]) == set(clean["order_id"])
    same_revenue = round(df["revenue"].sum(), 2) == round(clean["revenue"].sum(), 2)
    same_returns = (df["returned"] == "Y").sum() == (clean["returned"] == "Y").sum()
    print(f"Agrees with Module 6's shopkart_clean.csv: orders {same_orders}, "
          f"revenue {same_revenue}, returns {same_returns}")
    return same_orders and same_revenue and same_returns


def step_3_prepare(df):
    df = df.copy()
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["is_returned"] = (df["returned"] == "Y").astype(int)
    df["profit"] = df["revenue"] - df["quantity"] * df["cost_price"]
    df["delivery_band"] = pd.cut(df["delivery_days"], bins=[0, 3, 4, 5, 7, 30],
                                 labels=["2-3 days", "4 days", "5 days", "6-7 days", "8+ days"])
    overall_rate = df["is_returned"].mean()
    print("\nStep 3 - prepare columns")
    print(f"Overall return rate: {overall_rate:.1%}  ({df['is_returned'].sum()} of {len(df)} orders)")
    print(f"Total revenue: ₹{df['revenue'].sum():,.0f}   Total profit: ₹{df['profit'].sum():,.0f}")
    return df, overall_rate


def step_4_where(df, overall_rate, show_charts=True):
    print("\nStep 4 - where do returns happen?")
    tables = {}
    for number, (column, title, highlight, sort) in enumerate(CHARTS, start=1):
        table = tables[column] = return_table(df, column)
        print(f"\nChart {number} - return rate by {column}")
        print(table.sort_values("return_rate", ascending=False) if sort else table)
        if show_charts:
            fig = return_rate_bar(table, title, overall_rate, highlight=highlight, sort=sort)
            save_and_show(fig, MODULE, f"chart_{number}_return_rate_by_{column}.png")

    # Is Pune just slow? Lucknow and Jaipur are as slow, with normal return rates.
    check = df.groupby("city").agg(avg_delivery_days=("delivery_days", "mean"), return_rate=("is_returned", "mean"))
    check["return_rate"] = (check["return_rate"] * 100).round(1)
    print("\nIs Pune just slow? (slowest 4 cities)")
    print(check.round(2).sort_values("avg_delivery_days", ascending=False).head(4))

    df = df.assign(city_group=df["city"].where(df["city"] == "Pune", "Other cities"))
    pune_vs = (df.pivot_table(index="category", columns="city_group", values="is_returned") * 100).round(1)
    print("\nPune vs other cities, category by category (return rate %)")
    print(pune_vs)
    tables["pune_vs_others"] = pune_vs
    return tables


def step_5_money(df):
    """Revenue lost to returns = revenue of returned orders (assumption: full refund, no resale)."""
    returned = df[df["is_returned"] == 1]
    revenue_lost = returned["revenue"].sum()
    lost_by_city = returned.groupby("city")["revenue"].sum().sort_values(ascending=False).round(0)
    money = {
        "revenue_lost": revenue_lost,
        "profit_lost": returned["profit"].sum(),
        "share_of_revenue": revenue_lost / df["revenue"].sum(),
        "lost_by_city": lost_by_city,
        "lost_by_category": returned.groupby("category")["revenue"].sum().sort_values(ascending=False).round(0),
        "pune_share": lost_by_city["Pune"] / revenue_lost,
    }
    print("\nStep 5 - money")
    print(f"Revenue lost to returns: ₹{revenue_lost:,.0f}  ({money['share_of_revenue']:.1%} of all revenue)")
    print(f"Profit those returned orders would have made: ₹{money['profit_lost']:,.0f}")
    print("Revenue lost by city (₹):")
    print(lost_by_city)
    print(f"Pune share of revenue lost: {money['pune_share']:.1%}")
    return money


def step_6_predict(df, show_charts=True):
    print("\nStep 6 - can we predict returns?")
    X, y = return_features(df)
    X_train, X_test, y_train, y_test = split(X, y)
    baseline = baseline_accuracy(y_test)
    print("X shape:", X.shape, "| Train:", X_train.shape, " Test:", X_test.shape)
    print(f"Return rate in test set: {y_test.mean():.1%}")
    print(f"Baseline 'always not returned': accuracy {baseline:.1%}, recall 0%")

    models = return_models()
    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        r = results[name] = evaluate_classifier(model, X_test, y_test)
        print(f"\n{name}: accuracy {r['accuracy']:.3f}  precision {r['precision']:.3f}  recall {r['recall']:.3f}")
        print(r["confusion_matrix"])

    importance = pd.Series(models["Decision tree (depth 4)"].feature_importances_, index=X.columns)
    importance = importance.sort_values(ascending=False)
    print("\nWhat the tree relies on most:")
    print(importance.head(6).round(3))
    if show_charts:
        fig, ax = plt.subplots(figsize=(7, 3.5))
        top = importance.head(6)[::-1]
        ax.barh(top.index, top.values, color="#2A9D8F")
        ax.set_title("What the decision tree relies on most", loc="left")
        ax.set_xlabel("Feature importance")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        save_and_show(fig, MODULE, "chart_5_feature_importance.png")

    flags = flagging_summary(models["Logistic regression"], X_test, y_test)
    print(f"\nOrders flagged as risky: {flags['flagged']} of {flags['orders']} ({flags['flagged_share']:.0%})")
    print(f"Actual return rate among flagged orders:     {flags['return_rate_flagged']:.1%}")
    print(f"Actual return rate among NOT flagged orders: {flags['return_rate_not_flagged']:.1%}")
    return {"results": results, "flagging": flags, "importance": importance,
            "test_return_rate": y_test.mean(), "baseline_accuracy": baseline}


def lakh(rupees, decimals=1):
    """₹2,150,900 -> '₹21.5 lakh' (how the brief talks about money)."""
    return f"₹{rupees / 100000:.{decimals}f} lakh"


def step_7_insights(results):
    """The (insight, recommendation) pairs, with the numbers filled in from the analysis."""
    t, money, model = results["tables"], results["money"], results["model"]
    overall = results["overall_rate"] * 100
    cat, pay, band = t["category"], t["payment_mode"], t["delivery_band"]
    pune = t["city"].loc["Pune", "return_rate"]
    logreg, flags = model["results"]["Logistic regression"], model["flagging"]
    return [
        (f"Pune is the biggest leak: it returns {pune}% of orders vs {overall:.1f}% overall "
         f"(about {pune / overall:.1f}x), and loses {lakh(money['lost_by_city']['Pune'], 2)} "
         f"({money['pune_share']:.0%}) of the {lakh(money['revenue_lost'])} lost. Every category is worse in Pune.",
         "Operations audits the Pune courier partner and packaging this month; track Pune's return rate weekly."),
        (f"Slow delivery and COD raise returns: {band.loc['2-3 days', 'return_rate']}% at 2-3 days, "
         f"{band.loc['6-7 days', 'return_rate']}% at 6-7 days, {band.loc['8+ days', 'return_rate']}% at 8+ days. "
         f"COD {pay.loc['COD', 'return_rate']}% vs UPI {pay.loc['UPI', 'return_rate']}%.",
         "Faster delivery; a small UPI discount to move COD buyers to prepaid; confirm COD orders before shipping."),
        (f"Fashion returns most often ({cat.loc['Fashion', 'return_rate']}%, {cat.loc['Fashion', 'returns']} returns); "
         f"Electronics loses the most money ({lakh(money['lost_by_category']['Electronics'])}) because items cost more.",
         "Add size guides and real photos for Fashion; better product checks for Electronics."),
        (f"We can partly predict returns: logistic regression catches {logreg['recall']:.0%} of returns. "
         f"Orders it flags come back {flags['return_rate_flagged']:.1%} of the time vs "
         f"{flags['return_rate_not_flagged']:.1%} for the rest.",
         "Use the model to target confirmation calls, not to refuse orders."),
    ]


def analyse(show_charts=True):
    """Every capstone step in order. Returns everything the deck needs."""
    raw = step_1_load_with_sql()
    agrees = step_2_check(raw)
    df, overall_rate = step_3_prepare(raw)
    tables = step_4_where(df, overall_rate, show_charts)
    money = step_5_money(df)
    model = step_6_predict(df, show_charts)
    return {"df": df, "overall_rate": overall_rate, "agrees_with_module_6": agrees,
            "tables": tables, "money": money, "model": model}


if __name__ == "__main__":
    analyse()
    print("\nCharts saved in", module_output(MODULE))
