"""Video 4 project - The ShopKart SQL project (all business questions)
Run: python module_04_sql/lesson_4_9_module_project.py [--pause]
"""
import sys

from module_04_sql.sql_runner import run_file

run_file("M04_shopkart_sql_project.sql", pause="--pause" in sys.argv)
