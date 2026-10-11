"""Video 6.3 - Missing values, duplicates and types
Run: python module_06_pandas_eda/lesson_6_3_cleaning.py"""

import pandas as pd

from module_06_pandas_eda.cleaning import clean_orders
from project_paths import ORDERS_RAW, PRODUCTS, module_output

pd.set_option("display.width", 200, "display.max_columns", None)
df = pd.read_csv(ORDERS_RAW)
print(df.shape)

print("\n== Step 1 - Duplicates ==")
print("Duplicate rows:", df.duplicated().sum())
df = df.drop_duplicates()   # duplicates would double-count revenue
print("After dropping:", df.shape)
print("Duplicate order_ids left:", df["order_id"].duplicated().sum())

print("\n== Step 2 - City names ==")
print("Before:", df["city"].nunique(), "spellings")
df["city"] = df["city"].astype(str).str.strip().str.title()   # ' mumbai' -> 'Mumbai'
print("After strip + title:", df["city"].nunique())
df["city"] = df["city"].replace({"New Delhi": "Delhi", "Bangalore": "Bengaluru", "Bombay": "Mumbai",
                                 "Madras": "Chennai", "Calcutta": "Kolkata"})
print("After renaming:", df["city"].nunique())
print(df["city"].value_counts())

print("\n== Step 3 - unit_price: text to number ==")
print(df.loc[df["unit_price"].astype(str).str.contains("₹"), "unit_price"].head(3).tolist())
df["unit_price"] = (df["unit_price"].astype(str)
                    .str.replace("₹", "", regex=False)
                    .str.replace(",", "", regex=False)
                    .astype(float).astype(int))
print(df["unit_price"].dtype, df["unit_price"].min(), df["unit_price"].max())

print("\n== Step 4 - order_date: text to datetime ==")
# The dayfirst trap: format="mixed", dayfirst=True applies dayfirst to EVERY row,
# so 2025-01-02 (2 January) silently becomes 1 February.
demo = pd.Series(["2025-01-02", "2025-03-04", "02-01-2025"])
print(pd.to_datetime(demo, format="mixed", dayfirst=True))
trap = pd.to_datetime(df["order_date"], format="mixed", dayfirst=True)
iso = df["order_date"].str.match(r"^\d{4}-")
flipped = (trap[iso].dt.strftime("%Y-%m-%d") != df.loc[iso, "order_date"]).sum()
print("ISO dates read with day and month swapped:", flipped, "of", len(df))

# The safe way: ISO on every row (failures become NaT), then fill the gaps with DD-MM-YYYY
print("DD-MM-YYYY rows:", df["order_date"].str.contains(r"^\d{2}-").sum())
text_dates = df["order_date"].astype(str)
df["order_date"] = pd.to_datetime(text_dates, format="%Y-%m-%d", errors="coerce").fillna(
                   pd.to_datetime(text_dates, format="%d-%m-%Y", errors="coerce"))
print(df["order_date"].dtype)
print("Dates that failed both formats:", df["order_date"].isnull().sum())
print(df["order_date"].min(), "to", df["order_date"].max())

print("\n== Step 5 - payment_mode ==")
df["payment_mode"] = df["payment_mode"].replace({"upi": "UPI"}).fillna("Unknown")   # do not guess blanks
print(df["payment_mode"].value_counts())

print("\n== Step 6 - discount: blank means 0 ==")
print("Blank discounts:", df["discount"].isnull().sum())
df["discount"] = df["discount"].astype(float).fillna(0.0)
print("After:", df["discount"].isnull().sum())

print("\n== Step 7 - returned: one code ==")
df["returned"] = df["returned"].replace({"Yes": "Y", "No": "N"})
print(df["returned"].value_counts())

print("\n== Step 8 - quantity: typo or real outlier? ==")
products = pd.read_csv(PRODUCTS)
big = df[df["quantity"] >= 10].merge(products[["product_id", "product_name"]], on="product_id")
print(big[["order_id", "product_name", "quantity", "unit_price"]])
# The 99s are cheap everyday items (typo for 1). The 10s are Smartphones - a real bulk order, keep.
df.loc[df["quantity"] == 99, "quantity"] = 1
print(df["quantity"].value_counts().sort_index())

print("\n== Step 9 - rating: leave the gaps ==")
print("Missing ratings:", df["rating"].isnull().sum())
print("Average rating (pandas skips blanks):", round(df["rating"].mean(), 2))
# Filling with 0 would claim unhappy customers; filling with the mean would invent opinions.

print("\n== Final check and save ==")
print(df.shape)
print(df.isnull().sum())
df.info()
path = module_output("module_06") / "orders_clean.csv"
df.to_csv(path, index=False)
print("Saved", path)

print("\n== Practice ==")
print(round((df["payment_mode"] == "Unknown").mean() * 100, 1), "% Unknown")
print((df["city"] == "Pune").sum(), "Pune orders")

print("\n== The same steps, packaged as a function ==")
packaged = clean_orders(pd.read_csv(ORDERS_RAW))
pd.testing.assert_frame_equal(df, packaged)
print("clean_orders(raw) gives the same table as the steps above:", packaged.shape)
