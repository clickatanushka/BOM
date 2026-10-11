"""
Checks for the whole project:  python -m pytest -q

1. Every module runs on its own, in an EMPTY outputs folder (nothing left over from other modules).
2. The modules agree with each other and with the course's key numbers.
"""

import os
import subprocess
import sys
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_all import module_folders, scripts_for  # noqa: E402


@pytest.mark.parametrize("folder", [f for f in module_folders() if scripts_for(f)], ids=lambda f: f.name)
def test_module_runs_standalone(folder, tmp_path):
    env = dict(os.environ, MPLBACKEND="Agg", PYTHONWARNINGS="default", SHOPKART_OUTPUTS=str(tmp_path))
    for script in scripts_for(folder):
        result = subprocess.run([sys.executable, str(script)], cwd="/", env=env,
                                capture_output=True, text=True, stdin=subprocess.DEVNULL)
        assert result.returncode == 0, f"{script.name} failed:\n{result.stderr[-2000:]}"
        assert "Warning" not in result.stderr, f"{script.name} warned:\n{result.stderr[-2000:]}"


def quiet(function, *args, **kwargs):
    with redirect_stdout(StringIO()):
        return function(*args, **kwargs)


@pytest.fixture(scope="module")
def clean():
    from module_06_pandas_eda.cleaning import build_clean_table, load_raw
    return build_clean_table(*load_raw())


def test_module_6_matches_course_reference(clean, tmp_path):
    from module_06_pandas_eda.cleaning import final_checks
    from project_paths import REFERENCE_CLEAN_CSV
    assert all(final_checks(clean).values())
    clean.to_csv(tmp_path / "clean.csv", index=False)
    ours = pd.read_csv(tmp_path / "clean.csv")
    pd.testing.assert_frame_equal(ours, pd.read_csv(REFERENCE_CLEAN_CSV))


def test_key_numbers(clean):
    assert len(clean) == 5000
    assert round(clean["revenue"].sum(), 2) == 14704649.70
    assert round(clean["profit"].sum(), 2) == 3140749.70
    returned = clean["returned"] == "Y"
    assert returned.sum() == 687
    pune = clean[clean["city"] == "Pune"]
    assert (pune["returned"] == "Y").sum() == 146 and len(pune) == 451
    fashion = clean[clean["category"] == "Fashion"]
    assert round((fashion["returned"] == "Y").mean() * 100, 1) == 21.0
    assert round(clean.loc[returned, "revenue"].sum()) == 2150900


def test_sql_agrees_with_pandas(clean):
    from module_04_sql.sql_runner import run_query
    sql = run_query("SELECT COUNT(*) AS n, ROUND(SUM(quantity * unit_price * (1 - discount)), 2) AS revenue FROM orders")
    assert sql["n"][0] == 5000
    assert sql["revenue"][0] == round(clean["revenue"].sum(), 2)


def test_module_7_pipeline_reuses_module_6(tmp_path):
    from module_07_data_engineering import pipeline
    db = tmp_path / "warehouse.db"
    orders, customers, products = quiet(pipeline.extract)
    clean = quiet(pipeline.transform, orders, customers, products)
    quiet(pipeline.quality_checks, clean, expected_rows=orders["order_id"].nunique())
    quiet(pipeline.load, clean, customers, products, db=db, clean_csv=tmp_path / "clean.csv")
    added, skipped = quiet(pipeline.incremental_load, pipeline.NEW_ORDERS_FILE, db=db)
    assert (added, skipped) == (36, 2)
    sizes = quiet(pipeline.table_sizes, db=db)
    assert sizes["fact_orders"] == 5036 and sizes["dim_date"] == 357
    assert quiet(pipeline.incremental_load, pipeline.NEW_ORDERS_FILE, db=db)[0] == 0   # safe to rerun


def test_capstone_numbers():
    from module_10_capstone import capstone
    r = quiet(capstone.analyse, show_charts=False)
    assert r["agrees_with_module_6"]
    logreg = r["model"]["results"]["Logistic regression"]
    assert round(logreg["recall"], 3) == 0.555 and round(logreg["precision"], 3) == 0.209
    flags = r["model"]["flagging"]
    assert round(flags["return_rate_flagged"] * 100, 1) == 20.9
    assert round(flags["return_rate_not_flagged"] * 100, 1) == 9.6


def test_dashboard_tabs_work():
    """The finished-project dashboard: clean tab numbers, explore filters, a prediction, the findings."""
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "dashboard.py"), default_timeout=180).run()
    assert not at.exception
    metrics = [(m.label, m.value) for m in at.metric]
    assert ("Cities", "10") in metrics and ("Quality checks", "8 / 8 passed") in metrics
    assert ("Return rate", "13.7%") in metrics and ("Revenue of returned orders", "₹21,50,900") in metrics
    at.sidebar.multiselect[0].set_value(["Pune"]).run()
    assert ("Return rate", "32.4%") in [(m.label, m.value) for m in at.metric]
    at.button[0].click().run()
    assert not at.exception and "risk" in (at.success or at.error)[0].value
