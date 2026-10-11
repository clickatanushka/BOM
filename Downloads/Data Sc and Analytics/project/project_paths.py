"""
Where everything lives in the ShopKart project.

Every module imports its folders from here, so no script ever hard-codes a path
and every script works no matter which folder you run it from.

    from project_paths import DATA, OUTPUTS
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DATA = ROOT / "data"                      # the raw files from the course kit (never changed)
# Everything the modules produce. SHOPKART_OUTPUTS can point it somewhere else
# (the tests use that to prove each module runs on its own in an empty folder).
OUTPUTS = Path(os.environ.get("SHOPKART_OUTPUTS", ROOT / "outputs"))
OUTPUTS.mkdir(parents=True, exist_ok=True)

# Raw inputs
ORDERS_RAW = DATA / "orders_raw.csv"
CUSTOMERS = DATA / "customers.csv"
PRODUCTS = DATA / "products.csv"
NEW_ORDERS = DATA / "new_orders_2026_01.csv"
SHOPKART_DB = DATA / "shopkart.db"

# The file Module 6 creates and Modules 8 and 9 start from
CLEAN_CSV = OUTPUTS / "shopkart_clean.csv"

# Course reference copy of the clean file, used only to check our work
REFERENCE_CLEAN_CSV = DATA / "reference" / "shopkart_clean.csv"


def module_output(name):
    """A sub-folder of outputs/ for one module, e.g. module_output("module_08") -> outputs/module_08/."""
    folder = OUTPUTS / name
    folder.mkdir(parents=True, exist_ok=True)
    return folder
