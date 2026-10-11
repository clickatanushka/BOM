"""Video 5.1 - Why Python + Colab tour
Run: python module_05_python_basics/lesson_5_1_why_python.py"""

import pandas as pd

from project_paths import ORDERS_RAW

pd.set_option("display.max_columns", 20, "display.width", 160)

print("== 1. Text cells vs code cells ==")
# My first line of Python. Lines starting with # are comments - Python ignores them.
print("Welcome to ShopKart analytics!")

print("\n== 2. Python as a calculator ==")
print(2 * 1440)                 # order O10006: 2 pairs of Denim Jeans at ₹1,440 each
print(2 * 1440 * (1 - 0.05))    # with the customer's 5% discount
# Operators: + add, - subtract, * multiply, / divide, ** power, // whole-number division, % remainder

print("\n== 3. Only the last line shows (unless you print) ==")
# A notebook shows the last line of a cell by itself; a .py script shows nothing unless you print it.
1737.6 + 570.0          # not shown
print(1737.6 + 570.0)
print(2145.1 * 2)

print("\n== 4. Is our data there? A first peek at orders_raw.csv ==")
print(pd.read_csv(ORDERS_RAW).head())   # Module 6 material - it just proves the file is there

print("\n== Practice: order O10004, 2 Pressure Cookers at ₹2,020 with 15% discount ==")
print(2 * 2020 * (1 - 0.15))
