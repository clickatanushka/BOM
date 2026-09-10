# Rule-based baseline — D12 — test set

Rule: left vs right brightness asymmetry, sign +1, cut -0.0346, fitted on train+val.

| Metric | Rule-based |
|---|---|
| Images | 56 |
| False PASS | 0 |
| False FAIL | 0 |

Compare against the model numbers in `D12_test_report.md`. A rule that matches the model means the AI phase is not justified for this component; a rule that leaks reversed parts is the argument for it.
