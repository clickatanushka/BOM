"""Video 1.3 - Setup: tools and ShopKart
Run: python module_01_orientation/check_setup.py"""

import platform
import sqlite3
from contextlib import closing
from importlib.metadata import PackageNotFoundError, version

from project_paths import CUSTOMERS, NEW_ORDERS, ORDERS_RAW, PRODUCTS, REFERENCE_CLEAN_CSV, ROOT, SHOPKART_DB

CSV_FILES = {
    ORDERS_RAW: 5055,           # raw orders, messy on purpose (55 exact duplicates)
    CUSTOMERS: 800,
    PRODUCTS: 60,
    NEW_ORDERS: 40,             # January 2026 file, used in Module 7
    REFERENCE_CLEAN_CSV: 5000,  # course copy of the clean table, used to check Module 6
}
DB_TABLES = {"orders": 5000, "customers": 800, "products": 60}   # shopkart.db holds the cleaned data
results = {}

print("== 1. Python and libraries ==")
print(f"  {'Python':<14}{platform.python_version()}")
results["libraries"] = True
for name in ["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"]:
    try:
        print(f"  {name:<14}{version(name)}")
    except PackageNotFoundError:
        print(f"  {name:<14}MISSING  -> pip install -r requirements.txt")
        results["libraries"] = False

print("\n== 2. ShopKart data files ==")
import pandas as pd  # noqa: E402  imported here so a missing pandas is reported in step 1 first

results["data files"] = True
for path, expected in CSV_FILES.items():
    if not path.exists():
        print(f"  MISSING  {path.relative_to(ROOT)}")
        results["data files"] = False
        continue
    rows = len(pd.read_csv(path))
    results["data files"] &= rows == expected
    print(f"  {'OK' if rows == expected else 'WRONG':<8} {path.relative_to(ROOT)}: "
          f"{rows:,} rows (expected {expected:,})")

db = f"data/{SHOPKART_DB.name}"
if not SHOPKART_DB.exists():   # sqlite3.connect() would silently create an empty file
    print(f"  MISSING  {db}")
    results["data files"] = False
else:
    with closing(sqlite3.connect(SHOPKART_DB)) as con:   # closing() really closes the file
        for table, expected in DB_TABLES.items():
            try:
                rows = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            except sqlite3.Error as e:
                print(f"  WRONG    {db} table {table}: {e}")
                results["data files"] = False
                continue
            results["data files"] &= rows == expected
            print(f"  {'OK' if rows == expected else 'WRONG':<8} {db} table {table}: "
                  f"{rows:,} rows (expected {expected:,})")

print("\n== 3. First SQL query (what learners run at sqliteonline.com) ==")
try:
    from module_04_sql.sql_runner import run_query

    print("  SELECT * FROM orders LIMIT 5;")
    first5 = run_query("SELECT * FROM orders LIMIT 5;")
    print(first5.to_string(index=False))
    print("\n  SELECT COUNT(*) FROM orders;   (practice task 1.3)")
    count = int(run_query("SELECT COUNT(*) AS orders FROM orders;").iloc[0, 0])
    print(f"  -> {count:,}")
    print("  The raw file has 5,055 rows, the database 5,000: it holds the cleaned data (55 duplicates removed).")
    results["first SQL query"] = len(first5) == 5 and first5.iloc[0]["order_id"] == "O10001" and count == 5000
except Exception as e:   # e.g. missing database or library - report it instead of crashing
    print(f"  FAILED: {type(e).__name__}: {e}")
    results["first SQL query"] = False

print("\n== 4. First line of Python (what learners run in Colab) ==")
print("Hello, data!")
results["first Python line"] = True

print("\n== Summary ==")
for name, ok in results.items():
    print(f"  {'OK' if ok else 'FAIL':<5} {name}")
if all(results.values()):
    print("\nREADY - everything is set up, you can record.")
else:
    print("\nNOT READY - fix the FAIL lines above first.")
    raise SystemExit(1)
