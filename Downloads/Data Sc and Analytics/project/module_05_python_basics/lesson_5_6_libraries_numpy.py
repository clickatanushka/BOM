"""Video 5.6 - Libraries and NumPy
Run: python module_05_python_basics/lesson_5_6_libraries_numpy.py"""

import numpy as np
import pandas as pd

from project_paths import ORDERS_RAW

pd.set_option("display.max_columns", 20, "display.width", 160)

print("== 1. Libraries = ready-made toolboxes ==")
print("NumPy", np.__version__)
print("pandas", pd.__version__)   # your version number may differ - that is fine

print("\n== 2. The problem with plain lists ==")
prices_list = [362, 300, 2258, 2020, 1937, 1440, 15303, 14841]
qty_list = [6, 2, 1, 2, 2, 2, 2, 1]
totals = []
for p, q in zip(prices_list, qty_list):   # zip pairs items up
    totals.append(p * q)
print(totals)
print(prices_list * 2)   # this does NOT double the prices - it repeats the list!

print("\n== 3. NumPy arrays: maths on every value at once (vectorised) ==")
prices = np.array(prices_list)
qty = np.array(qty_list)
discount = np.array([0.20, 0.05, 0.05, 0.15, 0.10, 0.05, 0.20, 0.05])
gross = prices * qty                     # element by element, no loop
revenue = gross * (1 - discount)
print(gross)
print(revenue.round(2))
print("Total revenue:", revenue.sum().round(2))
print("Average order:", revenue.mean().round(2))
print("Biggest order:", revenue.max().round(2))
print("Median order:", np.median(revenue).round(2))
print(revenue >= 5000)
print(revenue[revenue >= 5000].round(2))
print("Count of big orders:", (revenue >= 5000).sum())
print((prices * 1.18).round(2))   # 18% GST on every price

print("\n== 4. pandas: NumPy arrays with column names = a table ==")
orders = pd.read_csv(ORDERS_RAW)
print(orders.shape)        # (rows, columns)
print(orders.head())
print("Average delivery days:", orders["delivery_days"].mean().round(2))
print("Largest quantity:", orders["quantity"].max())   # 99 items in one order? Suspicious!
# Some unit_price values are text like "₹1,299", so we cannot multiply yet - a Module 6 job.

print("\n== Practice: delivery days 4, 4, 2, 4, 2, 5, 3, 4 ==")
days = np.array([4, 4, 2, 4, 2, 5, 3, 4])
print(days.mean(), (days > 3).sum())
