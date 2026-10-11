"""Video 5.3 - Lists and dictionaries
Run: python module_05_python_basics/lesson_5_3_lists_dicts.py"""

import pandas as pd

print("== 1. Lists: many values in order ==")
order_amounts = [1737.6, 570.0, 2145.1, 3434.0, 3486.6, 2736.0]   # revenue of O10001 to O10006
print(order_amounts)
print(len(order_amounts))
print(sum(order_amounts))
print(max(order_amounts), min(order_amounts))
print(round(sum(order_amounts) / len(order_amounts), 2))   # average order value

print("\n== 2. Indexing and slicing (Python counts from 0) ==")
print(order_amounts[0])
print(order_amounts[-1])    # last
print(order_amounts[0:3])   # positions 0,1,2 (stop is NOT included)

cities = ["Delhi", "Chennai", "Delhi", "Lucknow"]
cities.append("Chennai")
print(cities)
print(cities.count("Delhi"))
print("Pune" in cities)
cities[3] = "Pune"          # position 3 is the 4th item
print(cities)
print(sorted(order_amounts, reverse=True))   # new list, original unchanged

print("\n== 3. Dictionaries: label -> value ==")
customer = {"customer_id": "C0593", "name": "Kavya Khan", "gender": "Female", "age": 26, "city": "Delhi",
            "membership": "Prime"}
print(customer["name"])
print(customer["membership"])
customer["age"] = 27
customer["orders_2025"] = 7   # a new key is simply added
print(customer.keys())
print(customer.get("phone", "not stored"))   # no error if the key is missing

print("\n== 4. A list of dictionaries is a mini table ==")
# Each dictionary = one row. Each key = one column name.
orders = [
    {"order_id": "O10001", "city": "Delhi",   "product": "Wings of Fire",   "revenue": 1737.6, "returned": "N"},
    {"order_id": "O10002", "city": "Chennai", "product": "Face Wash",       "revenue": 570.0,  "returned": "N"},
    {"order_id": "O10003", "city": "Delhi",   "product": "Saree",           "revenue": 2145.1, "returned": "N"},
    {"order_id": "O10004", "city": "Lucknow", "product": "Pressure Cooker", "revenue": 3434.0, "returned": "Y"},
]
print(len(orders), "rows")
print(orders[3]["product"], orders[3]["returned"])
print(pd.DataFrame(orders))   # sneak peek of Module 6

print("\n== Practice: product P009 Smartphone, margin per unit ==")
product = {"product_id": "P009", "product_name": "Smartphone", "category": "Electronics",
           "list_price": 14999, "cost_price": 11260}
print(product["list_price"] - product["cost_price"])
