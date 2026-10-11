"""Video 9.6 - Overfitting and next steps
Run: python module_09_machine_learning/lesson_9_6_overfitting_kmeans.py"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from module_06_pandas_eda.cleaning import load_clean
from module_09_machine_learning.models import LESSON_FEATURES, return_features, save_chart, split

df = load_clean()

# Same X, y and split as Video 9.4
X, y = return_features(df, LESSON_FEATURES)
X_train, X_test, y_train, y_test = split(X, y)
print("Train:", X_train.shape, " Test:", X_test.shape)

print("\n== 1. Overfitting demo ==")
# A deeper tree can memorise the training data; the test score tells the truth
results = []
for depth in range(1, 16):
    t = DecisionTreeClassifier(max_depth=depth, random_state=42)
    t.fit(X_train, y_train)
    results.append({"depth": depth, "train accuracy": t.score(X_train, y_train),
                    "test accuracy": t.score(X_test, y_test)})
res = pd.DataFrame(results).round(3)
print(res.to_string())

fig = plt.figure(figsize=(8, 4.5))
plt.plot(res["depth"], res["train accuracy"], marker="o", color="#2a78d6", label="Train")
plt.plot(res["depth"], res["test accuracy"], marker="o", color="#eb6834", label="Test")
plt.xlabel("Tree depth (max_depth)")
plt.ylabel("Accuracy")
plt.title("Deeper trees memorise the training data – test accuracy falls")
plt.xticks(range(1, 16))
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
save_chart(fig, "9_6_overfitting_depth")

full = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)   # no depth limit
print("Unlimited tree -> depth", full.get_depth(),
      "| train accuracy", round(full.score(X_train, y_train), 3),
      "| test accuracy", round(full.score(X_test, y_test), 3))
# Depth 1-3 underfits, 10+ overfits; choose depth by TEST (validation) performance

print("\n== 2. Bonus: unsupervised learning with K-Means ==")
# No target here - the algorithm finds groups of customers on its own
cust = df.groupby("customer_id").agg(orders=("order_id", "count"), total_spend=("revenue", "sum"),
                                     avg_discount=("discount", "mean"))
scaled = StandardScaler().fit_transform(cust)          # put the 3 columns on the same scale
cust["segment"] = KMeans(n_clusters=3, random_state=42, n_init=10).fit_predict(scaled)
print(cust.groupby("segment").agg(customers=("orders", "size"), avg_orders=("orders", "mean"),
                                  avg_spend=("total_spend", "mean"),
                                  avg_discount=("avg_discount", "mean")).round(2))
# One loyal high-value group, one deal-hunter group, one regular group.
# Segment numbers 0/1/2 are arbitrary labels; naming them is a human job.
