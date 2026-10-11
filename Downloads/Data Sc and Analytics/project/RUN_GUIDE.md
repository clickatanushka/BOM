# Run guide: every module, and what you should see

Every "you should see" line below is the real output of the scripts, so if your screen shows the same thing, it worked.

## Before you start (once per session)

Open a terminal in the `project` folder:

```bash
cd ~/Downloads/"Data Sc and Analytics"/project
```

Every command below starts from here. If you work inside an activated venv (`source .venv/bin/activate`), you can type `python` instead of `.venv/bin/python`.

**Charts:** a script with charts opens one window per chart and waits. Close the window (or press `q`) and it moves on. Every chart is also saved in `outputs/module_XX/`.

**Order:** you can run any module first. Modules that need the clean data rebuild it if it is missing.

---

## Module 1 – Orientation (setup check)

```bash
.venv/bin/python module_01_orientation/check_setup.py
```

| You should see | |
|---|---|
| Versions | Python 3.14.7, pandas 3.0.6, numpy 2.5.4, matplotlib 3.11.2, seaborn 0.13.2, scikit-learn 1.9.1 |
| Data files | orders_raw 5,055 rows, customers 800, products 60, new_orders_2026_01 40 |
| Database | orders 5,000 · customers 800 · products 60 |
| First SQL query | 5 orders starting with O10001, then `SELECT COUNT(*)` → 5000 |
| Last line | `READY - everything is set up, you can record.` |

If it says **NOT READY**, the lines marked FAIL above it say what is missing.

## Modules 2 and 3 – Excel and Statistics

No code (the course does these in Sheets). The spreadsheets are in `module_02_excel/` and `module_03_statistics/`.

## Module 4 – SQL

```bash
.venv/bin/python module_04_sql/lesson_4_1_explore_schema.py
.venv/bin/python module_04_sql/lesson_4_1_explore_schema.py --pause   # one query per Enter key
```

Each lesson prints every query, its result table, and `expected N  OK` under it. The last line tells you if all of them matched.

| Video | Script | Last line should say |
|---|---|---|
| 4.1 | `lesson_4_1_explore_schema.py` | 9 queries run, 9/9 match |
| 4.2 | `lesson_4_2_select_basics.py` | 9/9 (last result: 5000 orders, 758 customers who ordered) |
| 4.3 | `lesson_4_3_where_order_by.py` | 16/16 (Q4: Pune returns = 146) |
| 4.4 | `lesson_4_4_aggregates_group_by.py` | 12/12 |
| 4.5 | `lesson_4_5_inner_join.py` | 8/8 (last result: 5000 joined rows) |
| 4.6 | `lesson_4_6_left_join_three_tables.py` | 9/9 |
| 4.7 | `lesson_4_7_case_functions.py` | 9/9 (Fast ≤4 days: 10.9% returns, Slow: 18.4%) |
| 4.8 | `lesson_4_8_subqueries_cte_business_case.py` | 9/9 (Prime 9.79 orders per customer vs Free 4.77) |
| Project | `lesson_4_9_module_project.py` | 11/11 |

If a line says **MISMATCH**, the database file is not the course's `shopkart.db`.

## Module 5 – Python basics

```bash
.venv/bin/python module_05_python_basics/lesson_5_1_why_python.py
```

| Video | Script | Key output |
|---|---|---|
| 5.1 | `lesson_5_1_why_python.py` | first 5 rows of orders_raw.csv; practice answer `3434.0` |
| 5.2 | `lesson_5_2_variables_types.py` | `2736.0`, price 1299 → 2598, `Kolkata order revenue: ₹24484.8` |
| 5.3 | `lesson_5_3_lists_dicts.py` | total 14109.3, a 4-row table of orders, margin `3739` |
| 5.4 | `lesson_5_4_conditions_loops.py` | total 52693.05, messy city names cleaned in a loop, return rate 20%, practice: 4 orders under ₹3,000 |
| 5.5 | `lesson_5_5_functions_errors.py` | three error messages (TypeError, ValueError, KeyError) printed on purpose, `1399`, `Small Medium Big` |
| 5.6 | `lesson_5_6_libraries_numpy.py` | NumPy total 52693.05, raw file shape (5055, 12), average delivery 4.16 days, largest quantity 99 |
| Practice | `practice_solutions.py` | 10 exercises, last answer 14109.3 |

The error messages in 5.5 are part of the lesson. The script catches them and keeps going.

## Module 6 – Pandas & EDA

```bash
.venv/bin/python module_06_pandas_eda/lesson_6_1_load_inspect.py
```

| Video | Script | Key output |
|---|---|---|
| 6.1 | `lesson_6_1_load_inspect.py` | orders (5055, 12) · 27 city spellings · 55 duplicate rows |
| 6.2 | `lesson_6_2_select_filter_sort.py` | `city == 'Delhi'`: 715 · all Delhi spellings: 813 |
| 6.3 | `lesson_6_3_cleaning.py` | 5,000 rows, 10 cities · 120 DD-MM-YYYY dates · dayfirst trap flips 1,933 dates · 687 returns · 260 missing ratings · ends with "clean_orders(raw) gives the same table" |
| 6.4 | `lesson_6_4_new_columns.py` | revenue ₹14704649.7 · profit ₹3140749.7 · 241 loss-making orders · return rate 13.7% |
| 6.5 | `lesson_6_5_groupby_pivot.py` | Delhi ₹2323405 top city · Pune return rate 32.4% · October ₹1978317 best month |
| 6.6 | `lesson_6_6_merge.py` | 8 lines `OK ...` · `shopkart_clean.csv matches the course reference file` · 42 customers never ordered |
| 6.7 | `lesson_6_7_eda_5_questions.py` | Q1 October · Q2 Delhi 15.8% · Q3 Fashion 21.0% · Q4 discount vs quantity 0.27 · Q5 Prime 9.8 vs Free 4.8 orders per customer · **1 chart** |
| Practice | `practice_solutions.py` | COD 19.1%, delivery vs rating −0.33, Sunday 782 orders |

**Saved:** 6.3 saves `outputs/module_06/orders_clean.csv`. **6.6 saves `outputs/shopkart_clean.csv`, the file Modules 8 and 9 use.**

Packaged version: `.venv/bin/python module_06_pandas_eda/cleaning.py` runs all the cleaning in one go (8 OK checks, revenue ₹14,704,649.70).

## Module 7 – Data engineering

```bash
.venv/bin/python module_07_data_engineering/lesson_7_2_build_pipeline.py     # Video 7.2, step by step
.venv/bin/python module_07_data_engineering/pipeline.py                       # the "!python" moment: whole pipeline
```

What you should see in 7.2, in order:

1. `EXTRACT` 5,055 / 800 / 60 → `TRANSFORM` 5,055 raw rows → 5,000 clean rows, 21 columns.
2. 7 lines `PASS`, then a deliberately broken copy: `QUALITY CHECKS FAILED`, `PIPELINE STOPPED`, `Broken demo warehouse created? False`. The failure is part of the lesson.
3. `LOAD` fact_orders 5000, dim_customer 800, dim_product 60, dim_date 336.
4. First incremental load: **added 36 new orders, skipped 2**, 2 duplicate rows removed → fact_orders **5036**, dim_date **357**.
5. Second incremental load: **added 0**, skipped 38. It is safe to rerun.
6. Warehouse query: 2026 → 36 orders, ₹173149.15. Ends with `PIPELINE END success`.

**Saved:** `outputs/module_07/shopkart_warehouse.db`, `shopkart_clean.csv` (identical to Module 6's) and `pipeline_log.txt`.
**Practice:** `practice_solutions.py` ends with `Added: 3 | Skipped: 2` and fact_orders 5039.

Videos 7.1 and 7.3 have no code.

## Module 8 – Visualization

```bash
.venv/bin/python module_08_visualization/lesson_8_1_choosing_charts.py
```

| Video | Script | Key output | Charts |
|---|---|---|---|
| 8.1 | `lesson_8_1_choosing_charts.py` | overall return rate 13.7%, Pune 2.4× | 3 before/after makeovers (6 images) |
| 8.2 | `lesson_8_2_matplotlib.py` | median order 1524.8, mean 2940.93; 4,773 of 5,000 orders ≤ ₹10,000 | bar, line, histograms, two side by side |
| 8.3 | `lesson_8_3_seaborn.py` | slowest cities: Pune 5.77, Lucknow 5.75, Jaipur 5.63 days | countplots, barplot, boxplot, scatter, heatmap |
| 8.4 | `lesson_8_4_dashboard_kpis.py` | **Power BI KPIs:** revenue 14,704,649.70 · orders 5,000 · return rate 13.74% · avg rating 3.96 · profit 3,140,749.70 | dashboard mock-up |
| 8.5 | `lesson_8_5_story_charts.py` | Pune 32.4% (146 of 451), Pune Fashion 38.8% | 3 story charts |
| Practice | `practice_solutions.py` | Electronics 50% of revenue; Prime orders 2× as often | 4 charts |

**Saved:** all charts are in `outputs/module_08/`. For Power BI, load `outputs/module_08/shopkart_clean.csv`. To check your slicers, compare against `M08_dashboard_expected_kpis.csv` (for example, Pune → 32.37% returns, 451 orders).

## Module 9 – Machine learning

```bash
.venv/bin/python module_09_machine_learning/lesson_9_2_train_test_split.py
```

| Video | Script | Key output |
|---|---|---|
| 9.2 | `lesson_9_2_train_test_split.py` | 4,313 kept / 687 returned · return share train 13.75%, test 13.7% |
| 9.3 | `lesson_9_3_linear_regression.py` | Model MAE ₹2,403, R² 0.16 vs baseline MAE ₹2,438 · R² with unit_price ("cheating") 0.8 · 1 chart |
| 9.4 | `lesson_9_4_classification.py` | tree and logistic accuracy 86.1% · leaky tree 90.2% · ratings 4.15 kept vs 2.78 returned · 1 chart |
| 9.5 | `lesson_9_5_evaluation.py` | always-"no" model 86.3% vs ours 86.1% (the accuracy trap) · threshold table (0.20 → 179 flagged, recall 0.34) · 2 charts |
| 9.6 | `lesson_9_6_overfitting_kmeans.py` | unlimited tree: train 1.0, test 0.76 · K-Means segments of 292 / 252 / 214 customers · 1 chart |
| Practice | `practice_solutions.py` | best depth 1 (0.863), depth-15 gap 0.143 |

Video 9.1 has no code.

## Module 10 – Capstone

```bash
.venv/bin/python module_10_capstone/lesson_10_1_capstone_sql.py      # the capstone SQL (add --pause to step)
.venv/bin/python module_10_capstone/lesson_10_2_build_it.py          # Video 10.2
.venv/bin/python module_10_capstone/lesson_10_3_present_it.py        # Video 10.3: builds the deck
.venv/bin/python module_10_capstone/practice_solutions.py
```

| Script | Key output |
|---|---|
| 10.1 | `12 queries run, 12/12 match` (Q1 5000/800/60, Q2 687 returns = 13.7%, Q3b 5000 rows) |
| 10.2 | Step 1 SQL → (5000, 19) · Step 2 `Agrees with Module 6's shopkart_clean.csv: orders True, revenue True, returns True` · Step 3 13.7%, revenue ₹14,704,650 · Step 4 four return-rate charts (Pune 32.4%, Fashion 21.0%, COD 19.1%, 8+ days 30.3%) · Step 5 ₹2,150,900 lost (14.6%), Pune 25.0% of it · Step 6 logistic regression recall 0.555, precision 0.209; flagged 20.9% vs 9.6% · Step 7 four insights + actions |
| 10.3 | `Slide 1 … Slide 5` titles, then `Saved …/ShopKart_Returns_Story.pdf` |
| Practice | COD 983 orders, ₹571,925 returned · Pune COD 31.9% · depth 3/4/6 table · with rating: recall 0.885 (leakage) · Prime 13.2% vs Free 14.3% |

**Saved:** `outputs/module_10/`: 5 chart PNGs, `slide_1..5.png` and `ShopKart_Returns_Story.pdf`.

## Finale – the ShopKart Returns Dashboard (show this at the end)

```bash
.venv/bin/streamlit run dashboard.py
```

It opens in your browser (http://localhost:8501). What you should see:

| Tab | Check |
|---|---|
| 🧹 Before & after cleaning | Orders 5,000 (−55 duplicates from 5,055) · Cities 10 (−17 spellings from 27) · Rows fixed 1,119 · 8 / 8 checks. Table: dates 120, prices 150, cities 490, payment 150, discount 70, Yes/No 80, quantity 99 → 4, each with a real before → after (`02-01-2025`→`2025-01-02`, `₹2,551`→`2551`, `DELHI`→`Delhi`, ...) |
| 📊 Explore | Revenue ₹1,47,04,650 · 5,000 orders · 13.7% · ₹21,50,900 returned · 3.96 ★. Pune bar highlighted at 32.4%; revenue-by-month chart peaks in October. Sidebar City = Pune → 451 orders, 32.4% (+18.6 pts). Under 50 matching orders → "too few for reliable charts". |
| 🔮 Return risk predictor | Recall 55%, flagged 20.9% vs 9.6%. Default order (Beauty, Delhi, COD, 4 days, 10%, Free) → 44%, ✅ low risk. Fashion + Pune + COD + 8 days → 🚩 flag. |
| 💡 Findings | 4 insight cards (Pune 32.4%, COD 19.1%, Fashion 21.0%, model 55%), ₹21.5 lakh returned, slide viewer + PDF download |

Stop it with Ctrl+C in the terminal.

## Module 11 – Career

No code. `module_11_career/README_template.md` is the portfolio README template.

---

## Check everything at once

```bash
.venv/bin/python run_all.py          # all 43 scripts in course order, no chart windows -> "43/43 scripts passed"
.venv/bin/python run_all.py 6 7      # only some modules
.venv/bin/python -m pytest -q        # each module alone in an empty folder + key numbers -> "13 passed"
```

## If something goes wrong

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'module_06_pandas_eda'` (or `project_paths`) | You used a different Python. Use `.venv/bin/python`, or run `.venv/bin/pip install -e .` once. |
| Script seems stuck | A chart window is open (maybe behind the editor). Close it. |
| `--pause` waits | It is waiting for Enter. Ctrl+C stops it. |
| Want a clean start | Delete the `outputs/` folder; every module recreates what it needs. |
