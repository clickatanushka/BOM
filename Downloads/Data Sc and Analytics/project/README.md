# ShopKart – the course project, module by module

> **"Returns are eating our profit. What's going on, and can we predict them?"**

This folder is the Data Science & Analytics course project as plain Python files:
**one folder per module, one script per video**. Every module runs on its own, and each
module builds on the ones before it by *importing* their code, never by copying or editing it.

```
Module 4  sql_runner.py ──────────────────────────────────────────────┐
Module 6  cleaning.py ──► Module 7 pipeline.py (its T step)             │
              │                                                       ▼
              ├──► Module 8 charts.py ───────────────────────► Module 10 capstone.py
              └──► Module 9 models.py ───────────────────────►   (SQL → pandas → charts → model → deck)
```

## The finished project: ShopKart Returns Dashboard

```bash
.venv/bin/streamlit run dashboard.py
```

The finished project in 4 tabs, the same story the course tells:

| Tab | What it shows | Built from |
|---|---|---|
| 🧹 Before & after cleaning | 5,055 messy rows → 5,000 clean, 27 city spellings → 10, 8/8 checks, and a real row for each problem before → after | Module 6 cleaning |
| 📊 Explore | Sidebar filters (city, category, payment, membership, months); 5 KPI cards, return rate by city / category / payment / delivery time, revenue by month | Module 8 `return_table()` |
| 🔮 Return risk predictor | Enter a new order, get its return risk and whether to flag it | Module 9 model |
| 💡 Findings | The 4 insights with actions, and the 5-slide deck as a PDF | Module 10 capstone |

It imports the modules' own code, so every number matches the lessons. To share it, push the project to GitHub
and deploy `dashboard.py` on Streamlit Community Cloud (free); `requirements.txt` already lists everything it needs.

## One-time setup

```bash
cd project
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .          # lets every module import the earlier ones
.venv/bin/python module_01_orientation/check_setup.py     # should end with READY
```

The `.venv` in this folder is already set up, so on this machine only the last line is needed.

## Running a lesson

Run any script from anywhere:

```bash
.venv/bin/python module_06_pandas_eda/lesson_6_3_cleaning.py
```

- **Charts** open in a window. Close the window and the script carries on. Every chart is also saved in `outputs/module_XX/`.
- **SQL lessons** print each query, its result, and a check against the expected result written in the `.sql` file.
  Add `--pause` to step through one query per Enter key, which helps while recording.
- **Standalone:** any module can be run first. If a module needs `shopkart_clean.csv` and it does not exist yet,
  Module 6's `load_clean()` rebuilds it from the raw files automatically.

## What to run for each video

Full step-by-step commands with the output to expect for every script: **[RUN_GUIDE.md](RUN_GUIDE.md)**.

| Module | Video | Script |
|---|---|---|
| 1 Orientation | setup | `module_01_orientation/check_setup.py` |
| 2 Excel, 3 Statistics | – | No code by design. The course spreadsheets are copied into the folders. |
| 4 SQL | 4.1 – 4.8 | `module_04_sql/lesson_4_1_explore_schema.py` … `lesson_4_8_subqueries_cte_business_case.py` |
| | project | `module_04_sql/lesson_4_9_module_project.py` (the `.sql` files are in `module_04_sql/sql/`, and they also open in sqliteonline.com) |
| 5 Python basics | 5.1 – 5.6 | `module_05_python_basics/lesson_5_1_why_python.py` … `lesson_5_6_libraries_numpy.py` |
| 6 Pandas & EDA | 6.1 – 6.7 | `module_06_pandas_eda/lesson_6_1_load_inspect.py` … `lesson_6_7_eda_5_questions.py`. Lesson 6.6 writes `outputs/shopkart_clean.csv`. |
| | packaged | `module_06_pandas_eda/cleaning.py`: the 6.3 / 6.4 / 6.6 steps as functions that later modules reuse |
| 7 Data engineering | 7.2 | `module_07_data_engineering/lesson_7_2_build_pipeline.py` |
| | "!python" moment | `module_07_data_engineering/pipeline.py`: the whole pipeline in one command |
| 8 Visualization | 8.1 – 8.5 | `module_08_visualization/lesson_8_1_choosing_charts.py` … `lesson_8_5_story_charts.py` |
| 9 Machine learning | 9.2 – 9.6 | `module_09_machine_learning/lesson_9_2_train_test_split.py` … `lesson_9_6_overfitting_kmeans.py` |
| 10 Capstone | 10.1 | `module_10_capstone/lesson_10_1_capstone_sql.py` (the capstone `.sql`, through Module 4's runner) |
| | 10.2 | `module_10_capstone/lesson_10_2_build_it.py` |
| | 10.3 | `module_10_capstone/lesson_10_3_present_it.py`, which builds `outputs/module_10/ShopKart_Returns_Story.pdf` (5 slides) |
| 11 Career | – | `module_11_career/README_template.md` |

Modules 5–10 each also have a `practice_solutions.py`.
Videos 7.1, 7.3, 9.1 and 10.1's board work have no code.

## Run everything together

```bash
.venv/bin/python run_all.py            # all 43 scripts in course order (no chart windows)
.venv/bin/python run_all.py 8 9        # only Modules 8 and 9
.venv/bin/python run_all.py --fresh    # in an empty outputs folder
.venv/bin/python -m pytest -q          # each module alone in an empty folder + the key numbers
```

## Numbers every module agrees on

| Fact | Value | Where it shows up |
|---|---|---|
| Orders after cleaning | 5,000 (from 5,055 raw rows) | 4, 6, 7, 10 |
| Total revenue | ₹1,47,04,649.70 (same in SQL and pandas) | 4, 6, 7, 8 |
| Return rate | 13.7% (687 orders) | 4, 6, 8, 9, 10 |
| Pune | 32.4% (146 of 451), about 2.4× the average | 4, 6, 8, 10 |
| Fashion / COD | 21.0% / 19.1% | 6, 8, 10 |
| Revenue of returned orders | ₹21.5 lakh (14.6%) | 8, 10 |
| Warehouse after January | fact_orders 5,000 → 5,036, dim_date 336 → 357 | 7 |
| Capstone model | logistic regression recall 0.555, precision 0.209; flagged orders 20.9% vs 9.6% | 9, 10 |

## Folder layout

```
project/
  data/                 raw course files (never changed) + data/reference/ (course's clean CSV, for checking)
  outputs/              everything the scripts produce, one sub-folder per module
  project_paths.py      every file path in one place
  module_XX_*/          lessons, practice and that module's reusable file
  run_all.py, tests/    run / check everything
```

Library versions are newer than Colab's (pandas 3, scikit-learn 1.9). Where a notebook line needed a change
to run cleanly on them, the change is small, commented, and the numbers are unchanged.
