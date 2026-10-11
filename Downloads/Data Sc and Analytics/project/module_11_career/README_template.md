# <Project title, e.g. Why Members Leave FitGym – Churn Analysis & Prediction>

<One line: what you did and with which tools. e.g. "End-to-end analysis of 1,500 gym members using SQL, pandas and scikit-learn to explain and predict churn.">

![<Best chart – short description>](reports/charts/<chart_file>.png)

## Business question
<The question in one or two sentences, e.g. "Why are members leaving, and can we predict who will churn next?">

## Data
| File | Rows | Description |
|---|---|---|
| `data/members_raw.csv` | <rows> | <one line> |
| `data/plans.csv` | <rows> | <one line> |
| `data/fitgym.db` | – | <SQLite database with members and plans tables> |

Data issues found and fixed: <list, e.g. duplicate rows, branch spelling variants, Yes/No vs Y/N, impossible ages, missing visit counts>.

## Approach
1. **SQL** – <what you joined and why>
2. **Cleaning** – <main steps>
3. **EDA** – <what you compared: plan, trainer, visits, last visit, branch…>
4. **Money** – <your estimate and its assumption>
5. **Model** – <model(s), features, train/test split>
6. **Recommendations** – <for whom>

## Key findings
- <Finding 1 with a number>
- <Finding 2 with a number>
- <Finding 3 with a number>

## Model results (test set)
| Model | Accuracy | Precision | Recall |
|---|---|---|---|
| Baseline (always "not churned") | <..> | – | 0% |
| <Your model> | <..> | <..> | <..> |

<One sentence on what the model is good for and its limits.>

## Recommendations
1. <Action + who + expected effect>
2. <...>
3. <...>

## How to run
1. Open `notebooks/<notebook>.ipynb` in Google Colab (File → Upload notebook).
2. Upload the files from `data/` using the folder icon on the left.
3. Runtime → Run all.

## Repository structure
```
<repo-name>/
├── README.docx
├── data/            raw data + DATA_NOTE.md
├── sql/             <file>.sql
├── notebooks/       <file>.ipynb
├── reports/         slides PDF + charts/
└── requirements.txt
```

## Tools
SQL (SQLite) · Python (pandas, matplotlib, seaborn, scikit-learn) · Google Colab · <Google Sheets / Power BI if used>

## About me
<Your name> – <one line, e.g. "Aspiring data analyst, B.Com graduate">. [LinkedIn](<link>) · Certificate: Data Analytics, Data Engineering & Data Science – Zero to First Project (<Credential ID>)

---
### Filled example (course project ShopKart – for style only, write your own for FitGym)
**Key findings**
- 13.7% of 5,000 orders were returned; returned orders carried ₹21.5 lakh of revenue (14.6% of the total, assuming full refunds).
- Pune returned 32.4% of orders (about 2.4× average) and accounted for 25% of revenue lost.
- Returns rose from 10.4% (2–3 day delivery) to 30.3% (8+ days); COD 19.1% vs UPI 12.1%.

**Model results (1,000 test orders)**
| Model | Accuracy | Precision | Recall |
|---|---|---|---|
| Always "not returned" | 86.3% | – | 0% |
| Logistic regression (balanced) | 65.2% | 20.9% | 55.5% |
