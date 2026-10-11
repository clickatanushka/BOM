"""Video 4.4 - Aggregates, GROUP BY and HAVING
Run: python module_04_sql/lesson_4_4_aggregates_group_by.py [--pause]
"""
import sys

from module_04_sql.sql_runner import run_file

run_file("M04_4.4_aggregates_group_by.sql", pause="--pause" in sys.argv)
