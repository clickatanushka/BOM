"""Video 9.3 - Linear regression: predict order revenue
Run: python module_09_machine_learning/lesson_9_3_linear_regression.py"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from module_06_pandas_eda.cleaning import load_clean
from module_09_machine_learning.models import save_chart

df = load_clean()
y = df["revenue"]

print("\n== Step 1 - a one-feature model (the idea of a line) ==")
X1_train, X1_test, y_train, y_test = train_test_split(df[["quantity"]], y, test_size=0.2, random_state=42)
line = LinearRegression()
line.fit(X1_train, y_train)
print("Intercept:", round(line.intercept_, 0))
print("Slope    :", round(line.coef_[0], 0), "₹ extra per extra item")
print("R² on test:", round(line.score(X1_test, y_test), 3))
# R² near 0: quantity alone explains almost nothing (1 phone >> 3 books)

print("\n== Step 2 - prepare X with more features ==")
# revenue = quantity x unit_price x (1 - discount): giving the model unit_price is handing it the answer
X = pd.get_dummies(df[["category", "quantity", "discount", "membership", "city"]], drop_first=True, dtype=int)
print(X.shape)
print(X.head(3).to_string())
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(len(X_train), "train orders,", len(X_test), "test orders")

print("\n== Step 3 - fit the model and predict ==")
model = LinearRegression()
model.fit(X_train, y_train)
pred = model.predict(X_test)
print(pd.DataFrame({"actual ₹": y_test.values[:8], "predicted ₹": pred[:8].round(0)}))

print("\n== Step 4 - what did the model learn? (coefficients) ==")
# Rupees each feature adds/removes; category and city compared with Beauty / Ahmedabad
print("Intercept:", round(model.intercept_, 0))
print(pd.Series(model.coef_, index=X.columns).round(0).sort_values(ascending=False))

print("\n== Step 5 - evaluate in rupees ==")
# MAE = average miss in ₹, RMSE punishes big misses more, R² = share of variation explained
baseline = np.full(len(y_test), y_train.mean())     # always guess the average
print(f"Model    -> MAE ₹{mean_absolute_error(y_test, pred):,.0f} | "
      f"RMSE ₹{np.sqrt(mean_squared_error(y_test, pred)):,.0f} | R² {r2_score(y_test, pred):.2f}")
print(f"Baseline -> MAE ₹{mean_absolute_error(y_test, baseline):,.0f} | "
      f"RMSE ₹{np.sqrt(mean_squared_error(y_test, baseline)):,.0f} | R² 0.00")
print(f"R² on TRAIN data: {model.score(X_train, y_train):.2f}")

print("\n== What if we cheat and give it unit_price? ==")
a, b, c, d = train_test_split(df[["quantity", "unit_price", "discount"]], y, test_size=0.2, random_state=42)
cheat = LinearRegression().fit(a, c)
print("R² with unit_price:", round(cheat.score(b, d), 2))
# Not a better model - it just has part of the formula

fig = plt.figure(figsize=(6, 6))
plt.scatter(y_test, pred, alpha=0.3, s=10, color="#2a78d6")
plt.plot([0, 40000], [0, 40000], "--", color="black")     # a perfect model = this line
plt.xlim(0, 40000)
plt.ylim(0, 40000)
plt.xlabel("Actual revenue (₹)")
plt.ylabel("Predicted revenue (₹)")
plt.title("Predictions are rough: points are far from the line")
plt.tight_layout()
save_chart(fig, "9_3_predicted_vs_actual")
