"""Video 9.2-9.6 (practice) - Module 9 practice solutions
Run: python module_09_machine_learning/practice_solutions.py"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import confusion_matrix, mean_absolute_error, precision_score, r2_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from module_06_pandas_eda.cleaning import load_clean
from module_09_machine_learning.models import LESSON_FEATURES, return_features, split

df = load_clean()

print("\n== Task 1 - split (y = COD or not, 75/25, stratified) ==")
y_cod = (df["payment_mode"] == "COD").astype(int)
X_cod = pd.get_dummies(df[["category", "city", "unit_price", "membership", "age"]], drop_first=True, dtype=int)
a, b, c, d = train_test_split(X_cod, y_cod, test_size=0.25, random_state=42, stratify=y_cod)
print("COD share train:", round(c.mean() * 100, 1), "% | test:", round(d.mean() * 100, 1), "%")

print("\n== Task 2 - regression: predict profit ==")
Xp = pd.get_dummies(df[["category", "quantity", "discount", "membership", "city"]], drop_first=True, dtype=int)
a, b, c, d = train_test_split(Xp, df["profit"], test_size=0.2, random_state=42)
pp = LinearRegression().fit(a, c).predict(b)
print("MAE ₹", round(mean_absolute_error(d, pp)), "| R²", round(r2_score(d, pp), 2))
print("Baseline MAE ₹", round(mean_absolute_error(d, np.full(len(d), c.mean()))))
print("Interpretation: modest, like the revenue model – without the product price, profit is hard to predict.")

print("\n== Task 3 - leakage spotting ==")
base, y = return_features(df, LESSON_FEATURES)
for name, X in [("without rating", base),
                ("with rating", base.assign(rating=df["rating"].fillna(df["rating"].median())))]:
    a, b, c, d = split(X, y)
    t = DecisionTreeClassifier(max_depth=4, random_state=42).fit(a, c)
    print(name, "-> recall for returns:", round(recall_score(d, t.predict(b)), 2))
print("Answer: rating is leakage (given after the return decision). delivery_days, discount and "
      "order_month are known by shipping time. profit is not leakage for returns in this dataset, "
      "but it is just revenue minus cost - no new information.")

print("\n== Task 4 - threshold 0.25 ==")
a, b, c, d = split(base, y)
lr = make_pipeline(StandardScaler(), LogisticRegression()).fit(a, c)
p = (lr.predict_proba(b)[:, 1] >= 0.25).astype(int)
print(confusion_matrix(d, p))
print("precision", round(precision_score(d, p), 2), "| recall", round(recall_score(d, p), 2))

print("\n== Task 5 - overfitting: best max_depth ==")
trees = {dep: DecisionTreeClassifier(max_depth=dep, random_state=42).fit(a, c) for dep in range(1, 16)}
test_acc = {dep: t.score(b, d) for dep, t in trees.items()}
best = max(test_acc, key=test_acc.get)
print("Best depth:", best, "test accuracy", round(test_acc[best], 3))
print("Depth 15 gap (train - test):", round(trees[15].score(a, c) - trees[15].score(b, d), 3))
