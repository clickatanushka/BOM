"""Module 7 practice solutions (after Video 7.2) - extend the ShopKart pipeline
Run: python module_07_data_engineering/practice_solutions.py
"""

import sqlite3

import pandas as pd

from module_07_data_engineering.pipeline import (
    NEW_ORDERS_FILE, OUT, extract, incremental_load, load, quality_checks, table_sizes, transform,
)

# Its own warehouse, so the Video 7.2 warehouse stays at 5,036 orders. load() rebuilds it, so this is safe to rerun.
PRACTICE_DB = OUT / "practice_warehouse.db"
FEB_FILE = OUT / "new_orders_2026_02.csv"

print("== Build the warehouse first (same as Video 7.2) ==")
orders, customers, products = extract()
clean = transform(orders, customers, products)
quality_checks(clean, expected_rows=orders["order_id"].nunique())
load(clean, customers, products, db=PRACTICE_DB, clean_csv=OUT / "practice_clean.csv")
incremental_load(NEW_ORDERS_FILE, db=PRACTICE_DB)
print(table_sizes(PRACTICE_DB))


def extra_checks(df):
    checks = {
        "discount between 0 and 0.5": df["discount"].between(0, 0.5).all(),
        "rating 1-5 or blank": df["rating"].dropna().between(1, 5).all(),
    }
    for name, ok in checks.items():
        print("   ", "PASS" if ok else "FAIL", "-", name)
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise ValueError("Data quality check failed: " + "; ".join(failed))


print("\n== Task 1 - One more quality check ==")
extra_checks(clean)
broken = clean.copy()
broken.loc[0, "discount"] = 0.9
try:
    extra_checks(broken)
except ValueError as error:
    print("PIPELINE STOPPED ->", error)

print("\n== Task 2 - A new dimension table: dim_city ==")
dim_city = pd.DataFrame({
    "city":  ["Delhi", "Lucknow", "Jaipur", "Mumbai", "Pune", "Ahmedabad", "Bengaluru", "Hyderabad", "Chennai", "Kolkata"],
    "state": ["Delhi", "Uttar Pradesh", "Rajasthan", "Maharashtra", "Maharashtra", "Gujarat",
              "Karnataka", "Telangana", "Tamil Nadu", "West Bengal"],
    "zone":  ["North", "North", "North", "West", "West", "West", "South", "South", "South", "East"],
})
conn = sqlite3.connect(PRACTICE_DB)
dim_city.to_sql("dim_city", conn, if_exists="replace", index=False)

# every city in fact_orders must exist in dim_city, otherwise the JOIN would drop orders
missing = pd.read_sql("SELECT DISTINCT city FROM fact_orders WHERE city NOT IN (SELECT city FROM dim_city)", conn)
print("Cities missing from dim_city:", len(missing))
print(pd.read_sql("""
SELECT c.zone, COUNT(*) AS orders, ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_orders AS f
JOIN dim_city AS c ON f.city = c.city
JOIN dim_date AS d ON f.date_key = d.date_key
WHERE d.year = 2025
GROUP BY c.zone
ORDER BY revenue DESC
""", conn))

print("\n== Task 3 - Prime vs Free in January 2026 ==")
print(pd.read_sql("""
SELECT c.membership, COUNT(*) AS orders, ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_orders AS f
JOIN dim_customer AS c ON f.customer_id = c.customer_id
JOIN dim_date     AS d ON f.date_key    = d.date_key
WHERE d.year = 2026 AND d.month = 1
GROUP BY c.membership
""", conn))
conn.close()

# A late file: rows 3-5 become new February orders, rows 1-2 stay old 2025 orders
print("\n== Task 4 - A second new-orders file ==")
feb = pd.read_csv(NEW_ORDERS_FILE).head(5)
feb.loc[2:4, "order_id"] = ["O15037", "O15038", "O15039"]
feb.loc[2:4, "order_date"] = "2026-02-02"
feb.to_csv(FEB_FILE, index=False)
print(feb[["order_id", "order_date", "city", "unit_price"]])

added, skipped = incremental_load(FEB_FILE, db=PRACTICE_DB)
print("Added:", added, "| Skipped:", skipped)
print(table_sizes(PRACTICE_DB))
# Answer: 3 added (O15037-O15039), 2 skipped (O14999 and O15000 were loaded in 2025), one new date (2026-02-02).
