"""Module 7 - the ShopKart pipeline: Extract -> Transform (Module 6's build_clean_table) -> Quality checks -> Load.
Used by the Module 7 lesson, practice and tests. Run: python module_07_data_engineering/pipeline.py
"""

import io
import sqlite3
from datetime import datetime

import pandas as pd

from module_06_pandas_eda.cleaning import build_clean_table, load_raw
from project_paths import NEW_ORDERS, ORDERS_RAW, module_output

OUT = module_output("module_07")
NEW_ORDERS_FILE = NEW_ORDERS
WAREHOUSE_DB = OUT / "shopkart_warehouse.db"
CLEAN_CSV = OUT / "shopkart_clean.csv"
LOG_FILE = OUT / "pipeline_log.txt"

run_log = []


def log(message):
    line = datetime.now().strftime("%H:%M:%S") + "  " + message
    print(line)
    run_log.append(line)


def extract(orders_file=ORDERS_RAW):
    orders, customers, products = load_raw(orders_file)
    log(f"EXTRACT  {orders_file.name}: {len(orders)} rows | customers: {len(customers)} | products: {len(products)}")
    return orders, customers, products


def transform(orders, customers, products):
    df = build_clean_table(orders, customers, products)
    log(f"TRANSFORM  {len(orders)} raw rows -> {len(df)} clean rows, {df.shape[1]} columns")
    return df


def quality_checks(df, expected_rows):
    checks = {
        "row count = unique orders in source": len(df) == expected_rows,
        "no duplicate order_id": df["order_id"].is_unique,
        "no missing keys (order_id, customer_id, product_id, order_date)":
            df[["order_id", "customer_id", "product_id", "order_date"]].notnull().all().all(),
        "every product found in products.csv": df["category"].notnull().all(),
        "every customer found in customers.csv": df["membership"].notnull().all(),
        "unit_price > 0": (df["unit_price"] > 0).all(),
        "quantity between 1 and 10": df["quantity"].between(1, 10).all(),
    }
    for name, ok in checks.items():
        print("   ", "PASS" if ok else "FAIL", "-", name)
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        log(f"QUALITY CHECKS FAILED: {failed}")
        raise ValueError("Data quality check failed: " + "; ".join(failed) + ". Nothing was loaded.")
    log(f"QUALITY CHECKS  all {len(checks)} passed")


def make_dim_date(df):
    dates = df["order_date"].drop_duplicates().sort_values()
    return pd.DataFrame({
        "date_key": dates.dt.strftime("%Y%m%d").astype(int),   # 2025-01-31 -> 20250131
        "date": dates.dt.strftime("%Y-%m-%d"),
        "year": dates.dt.year,
        "month": dates.dt.month,
        "month_name": dates.dt.month_name(),
        "quarter": dates.dt.quarter,
        "weekday": dates.dt.day_name(),
        "is_weekend": dates.dt.dayofweek >= 5,
    })


def make_fact_orders(df):
    """Keys + numbers only: no product or customer names."""
    fact = df[["order_id", "customer_id", "product_id", "quantity", "unit_price", "discount",
               "city", "payment_mode", "delivery_days", "rating", "returned", "revenue", "profit"]].copy()
    fact.insert(1, "date_key", df["order_date"].dt.strftime("%Y%m%d").astype(int))
    return fact


def load(df, customers, products, db=WAREHOUSE_DB, clean_csv=CLEAN_CSV):
    # all 800 customers and 60 products go in, even those with no orders
    tables = {"fact_orders": make_fact_orders(df), "dim_customer": customers,
              "dim_product": products, "dim_date": make_dim_date(df)}
    conn = sqlite3.connect(db)
    for name, table in tables.items():
        table.to_sql(name, conn, if_exists="replace", index=False)
    conn.close()
    df.to_csv(clean_csv, index=False)
    sizes = ", ".join(f"{name} {len(table)}" for name, table in tables.items())
    log(f"LOAD  {db.name}: {sizes} rows | {clean_csv.name} {df.shape}")


def table_sizes(db=WAREHOUSE_DB):
    conn = sqlite3.connect(db)
    sizes = {t: int(pd.read_sql(f"SELECT COUNT(*) AS n FROM {t}", conn)["n"][0])
             for t in ["fact_orders", "dim_customer", "dim_product", "dim_date"]}
    conn.close()
    return sizes


def incremental_load(new_file, db=WAREHOUSE_DB):
    """Append only the orders (and dates) the warehouse has not seen, so it is safe to rerun."""
    log(f"INCREMENTAL LOAD  starting with {new_file.name}")
    new_raw, customers, products = extract(new_file)
    new_df = transform(new_raw, customers, products)
    quality_checks(new_df, expected_rows=new_raw["order_id"].nunique())

    conn = sqlite3.connect(db)
    loaded_ids = pd.read_sql("SELECT order_id FROM fact_orders", conn)["order_id"]
    to_add = new_df[~new_df["order_id"].isin(loaded_ids)]
    make_fact_orders(to_add).to_sql("fact_orders", conn, if_exists="append", index=False)
    known_dates = pd.read_sql("SELECT date_key FROM dim_date", conn)["date_key"]
    new_dates = make_dim_date(to_add)
    new_dates = new_dates[~new_dates["date_key"].isin(known_dates)]
    new_dates.to_sql("dim_date", conn, if_exists="append", index=False)
    conn.close()

    skipped = len(new_df) - len(to_add)
    log(f"INCREMENTAL LOAD  {len(new_raw)} rows in file, {len(new_raw) - len(new_df)} duplicate rows removed | "
        f"added {len(to_add)} new orders | skipped {skipped} already in warehouse | "
        f"added {len(new_dates)} new dates")
    return len(to_add), skipped


REVENUE_QUERY = """
SELECT d.year, d.month, p.category,
       COUNT(*)                 AS orders,
       ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_orders AS f
JOIN dim_product AS p ON f.product_id = p.product_id
JOIN dim_date    AS d ON f.date_key   = d.date_key
GROUP BY d.year, d.month, p.category
ORDER BY d.year, d.month, revenue DESC
"""


def query_warehouse(sql=REVENUE_QUERY, db=WAREHOUSE_DB):
    conn = sqlite3.connect(db)
    result = pd.read_sql(sql, conn)
    conn.close()
    return result


def same_as_module_6(clean_csv=CLEAN_CSV):
    """True if the pipeline's CSV equals Module 6's build_clean_table() output (raises if anything differs)."""
    module6 = build_clean_table(*load_raw())
    module6 = pd.read_csv(io.StringIO(module6.to_csv(index=False)))   # same CSV round trip as the file
    pd.testing.assert_frame_equal(pd.read_csv(clean_csv), module6)
    return True


def save_log(path=LOG_FILE):
    path.write_text("\n".join(run_log) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    log("PIPELINE START")
    orders, customers, products = extract()
    clean = transform(orders, customers, products)
    quality_checks(clean, expected_rows=orders["order_id"].nunique())
    load(clean, customers, products)
    if same_as_module_6():
        print("OK  shopkart_clean.csv is identical to the Module 6 cleaning output")
    incremental_load(NEW_ORDERS_FILE)
    log(f"WAREHOUSE TABLES  {table_sizes()}")

    result = query_warehouse()
    print("\nRevenue by category and month (last 10 rows):")
    print(result.tail(10).to_string(index=False))
    print("Revenue 2025: ₹", round(result.loc[result["year"] == 2025, "revenue"].sum(), 2),
          "| Revenue Jan 2026: ₹", round(result.loc[result["year"] == 2026, "revenue"].sum(), 2))
    log("PIPELINE END  success")
    print("\nRun log saved to", save_log())
