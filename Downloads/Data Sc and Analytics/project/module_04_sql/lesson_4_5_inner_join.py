"""Video 4.5 - INNER JOIN: combining two tables
Run: python module_04_sql/lesson_4_5_inner_join.py [--pause]
"""
import sys

from module_04_sql.sql_runner import run_file

run_file("M04_4.5_inner_join.sql", pause="--pause" in sys.argv)
