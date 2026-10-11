"""Video 10.1 - The brief -> plan, answered first in SQL (Q3 is the query lesson_10_2 runs from Python)
Run: python module_10_capstone/lesson_10_1_capstone_sql.py   (add --pause to step through the queries)"""

import sys
from pathlib import Path

from module_04_sql.sql_runner import run_file

run_file(Path(__file__).resolve().parent / "sql" / "M10_capstone_shopkart.sql", pause="--pause" in sys.argv)
