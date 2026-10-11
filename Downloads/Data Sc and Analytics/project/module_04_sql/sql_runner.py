"""
Module 4 - run SQL against shopkart.db from Python. Reused by Modules 1 and 10 and the tests.

run_query(sql)  -> a pandas DataFrame.
run_file(name)  -> runs every query in a .sql lesson file, printing its notes, result and a row-count check.

Run a lesson file:   python module_04_sql/sql_runner.py M04_4.2_select_basics.sql [--pause]
"""

import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

import pandas as pd

from project_paths import SHOPKART_DB

SQL_FOLDER = Path(__file__).resolve().parent / "sql"

pd.set_option("display.max_columns", 30, "display.width", 160)


def run_query(sql, db=SHOPKART_DB):
    with closing(sqlite3.connect(db)) as con:
        return pd.read_sql(sql, con)


def split_queries(text):
    """Split a .sql file into [{"notes": comment lines above it, "sql": ..., "expected_rows": int or None}]."""
    queries, notes, buffer = [], [], []
    for line in text.splitlines():
        stripped = line.strip()
        if not buffer and (stripped.startswith("--") or not stripped):
            # "-- Q3." starts a new note block, so the previous query's "Expected result" lines are not shown
            if re.match(r"--\s*Q\d+", stripped):
                notes = []
            if stripped and not re.match(r"--\s*[=-]{5,}", stripped):
                notes.append(line)
            match = re.match(r"--\s*Expected (?:result|output)\W*(\d+)\s+rows?", stripped)
            if match and queries and queries[-1]["expected_rows"] is None:
                queries[-1]["expected_rows"] = int(match.group(1))
            continue
        buffer.append(line)
        sql = "\n".join(buffer)
        if sqlite3.complete_statement(sql):
            queries.append({"notes": notes, "sql": sql.strip(), "expected_rows": None})
            notes, buffer = [], []
    return queries


def run_file(name, pause=False):
    """name is a file in module_04_sql/sql/, or a full path to any .sql file (Module 10 uses this)."""
    path = Path(name) if Path(name).is_file() else SQL_FOLDER / name
    queries = split_queries(path.read_text(encoding="utf-8"))
    checked = matched = 0
    with closing(sqlite3.connect(SHOPKART_DB)) as con:
        for number, q in enumerate(queries, start=1):
            print("=" * 78)
            print("\n".join(q["notes"]) or f"-- Query {number}")
            print()
            print(q["sql"])
            print("-" * 78)
            result = pd.read_sql(q["sql"], con)
            print(result.to_string(index=False, max_rows=20))
            line = f"({len(result)} row{'' if len(result) == 1 else 's'})"
            if q["expected_rows"] is not None:
                checked += 1
                ok = len(result) == q["expected_rows"]
                matched += ok
                line += f"  expected {q['expected_rows']}  {'OK' if ok else 'MISMATCH'}"
            print(line)
            if pause:
                input("\n[Enter] for the next query ")
    print("=" * 78)
    print(f"{path.name}: {len(queries)} queries run, {matched}/{checked} row counts match the expected results")
    return len(queries), checked, matched


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not names:
        print("Usage: python module_04_sql/sql_runner.py <file.sql> [--pause]")
        print("Files:", *sorted(p.name for p in SQL_FOLDER.glob("*.sql")), sep="\n  ")
    for name in names:
        run_file(name, pause="--pause" in sys.argv)
