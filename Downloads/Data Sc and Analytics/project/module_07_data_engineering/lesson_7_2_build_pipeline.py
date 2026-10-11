"""Video 7.2 - Build ShopKart's first pipeline in Python
Run: python module_07_data_engineering/lesson_7_2_build_pipeline.py
"""

import pandas as pd

from module_07_data_engineering.pipeline import (
    CLEAN_CSV, LOG_FILE, NEW_ORDERS_FILE, OUT, REVENUE_QUERY, WAREHOUSE_DB, extract, incremental_load, load, log,
    make_fact_orders, quality_checks, query_warehouse, run_log, same_as_module_6, save_log, table_sizes, transform,
)

# The broken-data demo points at its own warehouse, so the real one is never touched
BROKEN_DEMO_DB = OUT / "broken_demo_warehouse.db"

print("== The plan: settings and log() ==")
print("Warehouse:", WAREHOUSE_DB.name, "| Clean CSV:", CLEAN_CSV.name, "| Log:", LOG_FILE.name, "| all in", OUT)
log("PIPELINE START")

print("\n== Step 1 - Extract: read the sources as they are ==")
orders, customers, products = extract()

print("\n== Step 2 - Transform: the Module 6 cleaning inside one function ==")
clean = transform(orders, customers, products)
print(clean.head(3))

# A pipeline runs at 2 am when nobody is watching, so it checks its own work and stops before loading.
print("\n== Step 3 - Quality checks: stop if something looks wrong ==")
quality_checks(clean, expected_rows=orders["order_id"].nunique())

print("\n== What a failure looks like (a broken COPY of the clean data) ==")
broken = pd.concat([clean, clean.head(2)]).reset_index(drop=True)   # 2 orders now appear twice
broken.loc[5, "unit_price"] = 0
broken.loc[7, "customer_id"] = None
try:
    quality_checks(broken, expected_rows=5000)
    load(broken, customers, products, db=BROKEN_DEMO_DB, clean_csv=OUT / "broken_demo_clean.csv")
    print("Loaded")      # we never reach this line
except ValueError as error:
    print("PIPELINE STOPPED ->", error)
print("Broken demo warehouse created?", BROKEN_DEMO_DB.exists(), "-> nothing was loaded")

# Star schema: fact_orders in the centre, dim_customer, dim_product, dim_date around it.
print("\n== Step 4 - Load: a star schema in a SQLite warehouse ==")
print(make_fact_orders(clean).head(3))
load(clean, customers, products)
print(table_sizes())

print("\n== Did the pipeline reproduce Module 6? ==")
check = pd.read_csv(CLEAN_CSV)
print("shopkart_clean.csv:", check.shape)
print("Total revenue: ₹", round(check["revenue"].sum(), 2))
if same_as_module_6():
    print("Identical to the Module 6 file: same shape, columns and values")

# Reloading 5,000 old orders every month is slow, and blindly appending creates duplicates.
print("\n== Step 5 - Incremental load: January 2026 orders arrive ==")
new = pd.read_csv(NEW_ORDERS_FILE)
print("Rows in file:", len(new))
print("Exact duplicate rows:", new.duplicated().sum())
print("order_ids already loaded in 2025:", sorted(set(new["order_id"]) & set(clean["order_id"])))
print(new.head(6))
incremental_load(NEW_ORDERS_FILE)
print(table_sizes())

print("\n== Run it again: nothing should change (safe to re-run) ==")
added, skipped = incremental_load(NEW_ORDERS_FILE)
print("Added:", added, "| Skipped:", skipped)
print(table_sizes())

print("\n== Step 6 - Ask the warehouse a question with SQL ==")
print(REVENUE_QUERY)
result = query_warehouse(REVENUE_QUERY)
print(result.tail(10))
print(result.groupby("year")[["orders", "revenue"]].sum())   # 2025 should match Module 6 exactly

# When a pipeline breaks at night, the run log is the first file an engineer opens.
print("\n== Step 7 - The run log ==")
log("PIPELINE END  success")
print("\n".join(run_log))
print("Run log saved to", save_log())
