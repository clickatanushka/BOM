"""Video 5.5 - Functions and reading errors
Run: python module_05_python_basics/lesson_5_5_functions_errors.py"""


# def creates a recipe you can reuse. Inputs go in the brackets, return sends the answer back.
def calc_revenue(quantity, unit_price, discount=0):
    """Revenue for one order. discount is a fraction, e.g. 0.05 for 5%."""
    return round(quantity * unit_price * (1 - discount), 2)


def clean_price(price_text):
    """Turn '₹1,299' (or '1299') into the number 1299."""
    return int(str(price_text).replace("₹", "").replace(",", ""))


def clean_city(city):
    rename = {"New Delhi": "Delhi", "Bangalore": "Bengaluru", "Bombay": "Mumbai",
              "Madras": "Chennai", "Calcutta": "Kolkata"}
    city = city.strip().title()
    return rename.get(city, city)


def order_size(revenue):
    if revenue >= 5000:
        return "Big"
    elif revenue >= 1000:
        return "Medium"
    return "Small"


print("== 1. Your first function ==")
print(calc_revenue(2, 1440, 0.05))   # O10006 Denim Jeans
print(calc_revenue(6, 362, 0.2))     # O10001 Wings of Fire
print(calc_revenue(1, 2258))         # no discount given -> default 0
print(clean_price("₹1,299"), clean_price("₹2,551"), clean_price(1440))
for c in [" Mumbai", "Bombay", "DELHI", "Madras", "pune"]:
    print(repr(c), "->", clean_city(c))

print("\n== 2. Reading error messages ==")
# Read the LAST line first: error type and reason. Then look up for the line number.
# Error              Plain meaning                          Usual fix
# IndentationError   Spaces at line start are wrong         Indent 4 spaces after if, for, def
# NameError          Python never saw that name             Fix typo / run the earlier code
# TypeError          Wrong kind of value for this operation Convert with int(), float(), str()
# ValueError         Right kind, bad content                Clean the text first (remove ₹ and commas)
# KeyError           Key not in dictionary / table          Check spelling and capitals
# FileNotFoundError  File is not where Python looks         Check the path (here: project_paths.py)
# try / except is used below only so the script keeps running and prints the real message.
price = "₹1,299"     # text, as stored in orders_raw.csv
try:
    print(price + 100)   # TypeError
except Exception as e:
    print(type(e).__name__, ":", e)
print(clean_price(price) + 100)

try:
    int("₹1,299")        # ValueError
except Exception as e:
    print(type(e).__name__, ":", e)

customer = {"customer_id": "C0593", "name": "Kavya Khan", "city": "Delhi"}
try:
    customer["phone"]    # KeyError
except Exception as e:
    print(type(e).__name__, ":", e)

print("\n== Practice: order_size() ==")
print(order_size(570.0), order_size(3434.0), order_size(24484.8))
