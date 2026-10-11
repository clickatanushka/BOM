"""Video 4.2 - SELECT, FROM, LIMIT, aliases, DISTINCT
Run: python module_04_sql/lesson_4_2_select_basics.py [--pause]
"""
import sys

from module_04_sql.sql_runner import run_file

run_file("M04_4.2_select_basics.sql", pause="--pause" in sys.argv)
