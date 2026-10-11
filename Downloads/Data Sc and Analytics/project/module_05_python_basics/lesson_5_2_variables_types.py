"""Video 5.2 - Variables and data types
Run: python module_05_python_basics/lesson_5_2_variables_types.py"""

print("== 1. Variables are labelled boxes ==")
order_id = "O10006"     # str
city = "Delhi"          # str
quantity = 2            # int
unit_price = 1440       # int
discount = 0.05         # float
is_returned = False     # bool
print(order_id, city, quantity, unit_price, discount, is_returned)

print("\n== 2. Checking types with type() ==")
print(type(order_id))
print(type(quantity))
print(type(discount))
print(type(is_returned))

print("\n== 3. Calculating revenue ==")
revenue = quantity * unit_price * (1 - discount)   # same formula as the Excel column in Module 2
print(revenue)
print(type(revenue))   # int x int x float -> float
revenue = round(revenue, 2)
print(revenue)

print("\n== 4. f-strings: put variables inside a sentence ==")
print(f"Order {order_id} from {city}: revenue is ₹{revenue}")

print("\n== 5. Text that looks like a number is NOT a number ==")
messy_price = "₹1,299"   # 153 prices in orders_raw.csv look like this
print(type(messy_price))
clean_text = messy_price.replace("₹", "").replace(",", "")
print(clean_text, type(clean_text))
price = int(clean_text)
print(price, type(price))
print(price * 2)
print(float("0.05"), str(1440), int(2.9))   # int(2.9) is 2: it chops, it does not round

print("\n== 6. Useful string tricks for messy city names ==")
raw_city = " mumbai "
print(raw_city.strip())
print(raw_city.strip().title())
print("DELHI".title())
print("delhi" == "Delhi")        # False: Python is case-sensitive

print("\n== Practice: order O10007, 2 Smartphones at ₹15,303, 20% discount, '  kolkata' ==")
c = "  kolkata".strip().title()
rev = round(2 * 15303 * (1 - 0.20), 2)
print(f"{c} order revenue: ₹{rev}")
