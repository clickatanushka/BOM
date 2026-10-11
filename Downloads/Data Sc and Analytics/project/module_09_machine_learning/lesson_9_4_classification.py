"""Video 9.4 - Classification: will this order be returned?
Run: python module_09_machine_learning/lesson_9_4_classification.py"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree

from module_06_pandas_eda.cleaning import load_clean
from module_09_machine_learning.models import LESSON_FEATURES, return_features, save_chart, split

df = load_clean()

print("\n== Step 1 - prepare X, y and split (same as Video 9.2) ==")
X, y = return_features(df, LESSON_FEATURES)
X_train, X_test, y_train, y_test = split(X, y)
print("Train:", X_train.shape, " Test:", X_test.shape)
# No `rating`: it is given AFTER delivery, so using it is data leakage (Step 5)

print("\n== Step 2 - Decision Tree ==")
# A flowchart of yes/no questions; max_depth=4 = at most 4 questions in a row
tree = DecisionTreeClassifier(max_depth=4, random_state=42)
tree.fit(X_train, y_train)
tree_pred = tree.predict(X_test)
print("Tree accuracy on test:", round(tree.score(X_test, y_test) * 100, 1), "%")
print("Orders predicted 'returned':", tree_pred.sum(), "out of", len(tree_pred))
print(pd.Series(tree.feature_importances_, index=X.columns).sort_values(ascending=False).head(6).round(3))

print("\n== Step 3 - Logistic Regression ==")
# StandardScaler puts age and price on a similar scale
logreg = make_pipeline(StandardScaler(), LogisticRegression())
logreg.fit(X_train, y_train)
log_pred = logreg.predict(X_test)
print("Logistic accuracy on test:", round(logreg.score(X_test, y_test) * 100, 1), "%")
print("Orders predicted 'returned':", log_pred.sum(), "out of", len(log_pred))
# 86% accuracy but it almost never says 'returned' - the accuracy trap (Video 9.5)

print("\n== Step 4 - predict_proba: the probability of a return ==")
look = X_test[["delivery_days", "unit_price", "discount"]].copy()
look["city"] = df.loc[X_test.index, "city"]
look["payment_mode"] = df.loc[X_test.index, "payment_mode"]
look["P(return)"] = logreg.predict_proba(X_test)[:, 1].round(2)     # column 1 = probability of "returned"
look["actually returned"] = y_test.values
print(look.sort_values("P(return)", ascending=False, kind="stable").head(8).to_string())

# Do high-probability orders really get returned more? 4 equal groups of test orders
look["risk group"] = pd.qcut(look["P(return)"], 4, labels=["Lowest 25%", "Low-mid", "High-mid", "Highest 25%"])
print(look.groupby("risk group", observed=True)["actually returned"].agg(["count", "mean"])
      .rename(columns={"mean": "actual return rate"}).round(3))

print("\n== Step 5 - the data leakage trap (what if we add rating?) ==")
X_leak = X.copy()
X_leak["rating"] = df["rating"].fillna(df["rating"].median())
Xl_train, Xl_test, yl_train, yl_test = split(X_leak, y)
leaky = DecisionTreeClassifier(max_depth=4, random_state=42).fit(Xl_train, yl_train)
leaky_pred = leaky.predict(Xl_test)
print("Leaky tree accuracy:", round(leaky.score(Xl_test, yl_test) * 100, 1), "%")
print("Returns it catches :", leaky_pred[yl_test.values == 1].sum(), "of", yl_test.sum())
print()
print("Average rating of kept orders    :", round(df.loc[y == 0, "rating"].mean(), 2))
print("Average rating of returned orders:", round(df.loc[y == 1, "rating"].mean(), 2))
# Looks better, but there is no rating when the order ships -> unusable

fig = plt.figure(figsize=(18, 7))
plot_tree(tree, feature_names=list(X.columns), class_names=["Kept", "Returned"],
          filled=True, max_depth=2, fontsize=9, impurity=False, proportion=True)
plt.title("Top of the decision tree (first 2 levels)")
save_chart(fig, "9_4_decision_tree_top")
