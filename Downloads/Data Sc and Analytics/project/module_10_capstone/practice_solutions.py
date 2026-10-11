"""Module 10 - Practice solutions (extension tasks on the capstone data)
Run: python module_10_capstone/practice_solutions.py"""

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from module_04_sql.sql_runner import run_query
from module_09_machine_learning.models import evaluate_classifier, return_features, split
from module_10_capstone import capstone

df, _ = capstone.step_3_prepare(capstone.step_1_load_with_sql())
print()

print("== Task 1 - How big is the COD problem? ==")
cod = df[df["payment_mode"] == "COD"]
rate = df.groupby("payment_mode")["is_returned"].mean() * 100
print(f"COD orders: {len(cod)} of {len(df):,}")
print(f"COD return rate {rate['COD']:.1f}% vs UPI {rate['UPI']:.1f}%")
print(f"Revenue of returned COD orders: ₹{cod.loc[cod['is_returned'] == 1, 'revenue'].sum():,.0f}")

print("\n== Task 2 - Is it a city effect? COD return rate, Pune vs the rest (SQL) ==")
print(run_query("""
SELECT CASE WHEN city = 'Pune' THEN 'Pune' ELSE 'Other cities' END AS city_group,
       COUNT(*) AS cod_orders,
       ROUND(AVG(CASE WHEN returned = 'Y' THEN 1.0 ELSE 0 END) * 100, 1) AS return_rate_pct
FROM orders
WHERE payment_mode = 'COD'
GROUP BY city_group;
""").to_string(index=False))
print("COD is worse than prepaid everywhere, and Pune is bad whether or not the order is COD.")

print("\n== Task 3 - Decision tree depth 3 / 4 / 6 ==")
X_train, X_test, y_train, y_test = split(*return_features(df))
rows = []
for depth in [3, 4, 6]:
    tree = DecisionTreeClassifier(max_depth=depth, class_weight="balanced", random_state=42).fit(X_train, y_train)
    r = evaluate_classifier(tree, X_test, y_test)
    rows.append({"max_depth": depth, "accuracy": round(r["accuracy"], 3), "precision": round(r["precision"], 3),
                 "recall": round(r["recall"], 3), "false_alarms": int(r["confusion_matrix"][0, 1])})
print(pd.DataFrame(rows).to_string(index=False))
print("Deeper catches more returns but raises many more false alarms - pick with the cost of each in mind.")

print("\n== Task 4 - What if we (wrongly) add rating? ==")
features = ["category", "city", "payment_mode", "delivery_days", "discount", "membership", "rating"]
leaky = df.dropna(subset=["rating"])          # only rated orders (260 were never rated)
X_train, X_test, y_train, y_test = split(*return_features(leaky, features))
tree = DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=42).fit(X_train, y_train)
r = evaluate_classifier(tree, X_test, y_test)
print(f"With rating: recall {r['recall']:.3f}, precision {r['precision']:.3f}, accuracy {r['accuracy']:.3f}")
print("Average rating:", df.groupby("returned")["rating"].mean().round(1).to_dict())
print("Looks great, but rating is given after delivery (often with the return) - it does not exist at order time.")
print("That is data leakage: the model could never be used on a new order.")

lost_by_category = capstone.step_5_money(df)["lost_by_category"]
print("\n== Task 5 - Revenue lost by category ==")
print(lost_by_category.apply(lambda v: f"₹{v:,.0f}").to_string())
print("Electronics loses the most money even though Fashion has the higher return rate.")

print("\n== Task 6 - Prime vs Free return rate ==")
print((df.groupby("membership")["is_returned"].mean() * 100).round(1).to_string())
print("About one point apart - 'membership does not matter much' is also a finding.")
