"""Video 4.1 - What is a database? Keys and schema
Run: python module_04_sql/lesson_4_1_explore_schema.py [--pause]
"""
import sys

from module_04_sql.sql_runner import run_file

run_file("M04_4.1_explore_schema.sql", pause="--pause" in sys.argv)
