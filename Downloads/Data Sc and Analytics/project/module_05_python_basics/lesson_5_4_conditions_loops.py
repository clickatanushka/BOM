"""Video 5.4 - Conditions and loops
Run: python module_05_python_basics/lesson_5_4_conditions_loops.py"""

print("== 1. if / elif / else ==")
revenue = 3434.0
if revenue >= 5000:
    size = "Big"
elif revenue >= 1000:
    size = "Medium"
else:
    size = "Small"
print(size)

# Comparison operators: == != > < >= <=, combined with and / or / not
city = "Pune"
payment_mode = "COD"
if city == "Pune" and payment_mode == "COD":
    print("Flag for return-risk check")

print("\n== 2. for loops: do the same thing for every item ==")
order_amounts = [1737.6, 570.0, 2145.1, 3434.0, 3486.6, 2736.0, 24484.8, 14098.95]
for amount in order_amounts:
    print(amount)

# Running total and counting big orders - what SUM and COUNTIF do in Excel
total = 0
big_orders = 0
for amount in order_amounts:
    total = total + amount
    if amount >= 5000:
        big_orders = big_orders + 1
print("Total:", round(total, 2))
print("Big orders:", big_orders)

print("\n== 3. Building a new list inside a loop ==")
sizes = []
for amount in order_amounts:
    if amount >= 5000:
        sizes.append("Big")
    elif amount >= 1000:
        sizes.append("Medium")
    else:
        sizes.append("Small")
print(sizes)

print("\n== 4. Loop over a mini table: cleaning messy city names ==")
raw_cities = ["delhi", "New Delhi", "Delhi ", "DELHI", "Bangalore", "Bombay", " Mumbai", "Madras", "Calcutta", "pune"]
rename = {"New Delhi": "Delhi", "Bangalore": "Bengaluru", "Bombay": "Mumbai", "Madras": "Chennai", "Calcutta": "Kolkata"}
clean_cities = []
for c in raw_cities:
    c = c.strip().title()
    c = rename.get(c, c)           # swap an old name if it is in the dictionary, else keep it
    clean_cities.append(c)
print(clean_cities)

print("\n== 5. Looping over a list of dictionaries: return rate ==")
orders = [
    {"order_id": "O10001", "city": "Delhi",   "returned": "N"},
    {"order_id": "O10002", "city": "Chennai", "returned": "N"},
    {"order_id": "O10003", "city": "Delhi",   "returned": "N"},
    {"order_id": "O10004", "city": "Lucknow", "returned": "Y"},
    {"order_id": "O10005", "city": "Chennai", "returned": "N"},
]
returns = 0
for order in orders:
    if order["returned"] == "Y":
        returns += 1                 # short for returns = returns + 1
print(f"Return rate: {returns / len(orders):.0%}")

print("\n== 6. range() and while (quick look) ==")
for i in range(3):          # 0, 1, 2
    print("Order number", i + 1)

stock = 5                   # Smartphones in the warehouse; each order takes 2
while stock >= 2:
    stock = stock - 2
    print("Stock left:", stock)

print("\n== Practice: orders under ₹3,000 ==")
small = []
for amount in order_amounts:
    if amount < 3000:
        small.append(amount)
print(small, len(small))
