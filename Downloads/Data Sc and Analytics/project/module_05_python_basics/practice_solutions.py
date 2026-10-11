"""Module 5 practice - solutions
Run: python module_05_python_basics/practice_solutions.py"""

import numpy as np


def profit(quantity, unit_price, discount, cost_price):
    """Exercise 9: revenue minus quantity x cost_price."""
    revenue = round(quantity * unit_price * (1 - discount), 2)
    return round(revenue - quantity * cost_price, 2)


print("== Exercise 1 - Revenue of one order (O10009: 2 Tablets at ₹18,548, 5% off) ==")
print(round(2 * 18548 * (1 - 0.05), 2))

print("\n== Exercise 2 - Types ==")
for value in ["O10009", 18548, 0.05, True]:
    print(value, type(value))

print("\n== Exercise 3 - Clean a messy price (O10041: '₹2,551', quantity 3) ==")
price = int("₹2,551".replace("₹", "").replace(",", ""))
print(price * 3)

print("\n== Exercise 4 - f-string receipt ==")
name = "Yash Khan"
city = "Chennai"
revenue = 570.0
print(f"{name} from {city} paid ₹{revenue}")

print("\n== Exercise 5 - List statistics ==")
ratings = [2, 5, 3, 4, 4, 4, 5, 4, 5, 3]
print(sum(ratings) / len(ratings))
print(ratings.count(5))

print("\n== Exercise 6 - Dictionary update ==")
customer = {"customer_id": "C0367", "name": "Yash Khan", "age": 35, "city": "Chennai", "membership": "Free"}
customer["membership"] = "Prime"
print(customer)

print("\n== Exercise 7 - if/elif/else ==")
delivery_days = 6
if delivery_days <= 3:
    label = "Fast"
elif delivery_days <= 5:
    label = "Normal"
else:
    label = "Slow"
print(label)

print("\n== Exercise 8 - Loop and count ==")
payments = ["COD", "Debit Card", "Debit Card", "COD", "UPI", "UPI", "UPI", "Credit Card", "Debit Card", "Credit Card"]
upi = 0
for p in payments:
    if p == "UPI":
        upi += 1
print(upi)

print("\n== Exercise 9 - Function ==")
print(profit(6, 362, 0.2, 240))   # O10001: 6 x Wings of Fire, ₹362, 20% off, cost ₹240

print("\n== Exercise 10 - NumPy ==")
rev = np.array([1737.6, 570.0, 2145.1, 3434.0, 3486.6, 2736.0])
print(rev.sum().round(2))
print(rev[rev > 2500])
