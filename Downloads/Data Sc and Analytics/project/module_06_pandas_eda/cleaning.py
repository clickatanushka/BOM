"""
Module 6 - the ShopKart cleaning from lessons 6.3, 6.4 and 6.6, packaged as functions.
Reused by Module 7 (build_clean_table), Modules 8, 9, 10 (load_clean) and the tests.
Run: python module_06_pandas_eda/cleaning.py
"""

import pandas as pd

from project_paths import CLEAN_CSV, CUSTOMERS, ORDERS_RAW, PRODUCTS

CITY_FIXES = {"New Delhi": "Delhi", "Bangalore": "Bengaluru", "Bombay": "Mumbai",
              "Madras": "Chennai", "Calcutta": "Kolkata"}


def load_raw(orders_file=ORDERS_RAW):
    return pd.read_csv(orders_file), pd.read_csv(CUSTOMERS), pd.read_csv(PRODUCTS)


def clean_orders(orders):
    """Lesson 6.3 steps 1-9 (rating keeps its blanks: "not rated" is real information)."""
    df = orders.drop_duplicates()
    df["city"] = df["city"].astype(str).str.strip().str.title().replace(CITY_FIXES)
    df["unit_price"] = (df["unit_price"].astype(str)
                        .str.replace("₹", "", regex=False)
                        .str.replace(",", "", regex=False)
                        .astype(float).astype(int))
    # ISO first, then DD-MM-YYYY (format="mixed", dayfirst=True would flip 2025-01-02 to 1 Feb)
    text_dates = df["order_date"].astype(str)
    df["order_date"] = pd.to_datetime(text_dates, format="%Y-%m-%d", errors="coerce").fillna(
                       pd.to_datetime(text_dates, format="%d-%m-%Y", errors="coerce"))
    df["payment_mode"] = df["payment_mode"].replace({"upi": "UPI"}).fillna("Unknown")
    df["discount"] = df["discount"].astype(float).fillna(0.0)
    df["returned"] = df["returned"].replace({"Yes": "Y", "No": "N"})
    df.loc[df["quantity"] == 99, "quantity"] = 1   # typo for 1; the real bulk orders of 10 stay
    return df


def add_details(df, customers, products):
    """Lesson 6.6: LEFT joins keep every order."""
    out = df.merge(products[["product_id", "product_name", "category", "cost_price"]], on="product_id", how="left")
    out = out.merge(customers[["customer_id", "gender", "age", "membership"]], on="customer_id", how="left")
    assert len(out) == len(df), "Row count changed during merge!"
    return out


def add_columns(df):
    """Lesson 6.4: revenue, profit and order month."""
    df = df.copy()
    df["revenue"] = (df["quantity"] * df["unit_price"] * (1 - df["discount"])).round(2)
    df["profit"] = df["revenue"] - df["quantity"] * df["cost_price"]
    df["order_month"] = df["order_date"].dt.month
    return df


def build_clean_table(orders, customers, products):
    return add_columns(add_details(clean_orders(orders), customers, products))


def final_checks(df):
    return {
        "5,000 rows": len(df) == 5000,
        "21 columns": df.shape[1] == 21,
        "no duplicate order_id": df["order_id"].is_unique,
        "10 cities": df["city"].nunique() == 10,
        "no quantity 99": (df["quantity"] != 99).all(),
        "all dates parsed": df["order_date"].notnull().all(),
        "only Y/N in returned": set(df["returned"]) == {"Y", "N"},
        "only rating has blanks": df.drop(columns="rating").isnull().sum().sum() == 0,
    }


def save_clean(df, path=CLEAN_CSV):
    df.to_csv(path, index=False)
    return path


def load_clean(rebuild=False):
    """The cleaned orders; builds and saves the file first if no earlier module made it."""
    if rebuild or not CLEAN_CSV.exists():
        df = build_clean_table(*load_raw())
        save_clean(df)
        return df
    return pd.read_csv(CLEAN_CSV, parse_dates=["order_date"])


if __name__ == "__main__":
    orders, customers, products = load_raw()
    print("Raw orders:", orders.shape)
    df = build_clean_table(orders, customers, products)
    for name, ok in final_checks(df).items():
        print("OK  " if ok else "FAIL", name)
    print(f"Saved {save_clean(df).name} {df.shape}")
    print(f"Total revenue: ₹{df['revenue'].sum():,.2f} | Total profit: ₹{df['profit'].sum():,.2f}")
