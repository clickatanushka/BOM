"""Video 9.5 - Evaluating classifiers
Run: python module_09_machine_learning/lesson_9_5_evaluation.py"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, classification_report,
                             confusion_matrix, f1_score, precision_score, recall_score)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from module_06_pandas_eda.cleaning import load_clean
from module_09_machine_learning.models import LESSON_FEATURES, return_features, save_chart, split

# Same X, y, split and logistic regression as Video 9.4
X, y = return_features(load_clean(), LESSON_FEATURES)
X_train, X_test, y_train, y_test = split(X, y)
print("Train:", X_train.shape, " Test:", X_test.shape)
logreg = make_pipeline(StandardScaler(), LogisticRegression())
logreg.fit(X_train, y_train)
pred = logreg.predict(X_test)
proba = logreg.predict_proba(X_test)[:, 1]

print("\n== 1. The accuracy trap ==")
always_no = np.zeros(len(y_test), dtype=int)     # a 'dumb model' that ALWAYS says "not returned"
print("Dumb model accuracy  :", round(accuracy_score(y_test, always_no) * 100, 1), "%")
print("Our model accuracy   :", round(accuracy_score(y_test, pred) * 100, 1), "%")
print("Returns in test set  :", y_test.sum(), "of", len(y_test))

print("\n== 2. The confusion matrix ==")
# rows = actual (kept, returned), columns = predicted (kept, returned)
cm = confusion_matrix(y_test, pred)
print(cm)
tn, fp, fn, tp = cm.ravel()
print(f"TN={tn}  FP={fp}  FN={fn}  TP={tp}")

print("\n== 3. Precision, recall, F1 ==")
# Precision = TP/(TP+FP): when it says 'return', is it right?
# Recall    = TP/(TP+FN): of all real returns, how many did we catch?
print(classification_report(y_test, pred, target_names=["Kept", "Returned"], zero_division=0))
# At threshold 0.5 recall for 'Returned' is 0 - useless, even with 86% accuracy

print("\n== 4. Threshold tuning ==")
# Lower threshold -> more returns caught (recall up), more false alarms (precision down)
rows = []
for t in [0.5, 0.3, 0.2, 0.15]:
    p = (proba >= t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, p).ravel()
    rows.append({"threshold": t, "flagged orders": tp + fp, "returns caught (TP)": tp, "false alarms (FP)": fp,
                 "precision": round(precision_score(y_test, p, zero_division=0), 2),
                 "recall": round(recall_score(y_test, p), 2),
                 "F1": round(f1_score(y_test, p), 2),
                 "accuracy": round(accuracy_score(y_test, p), 2)})
print(pd.DataFrame(rows).to_string())
# Accuracy goes DOWN as the model gets more useful; the threshold is a business decision

for t, note in [(0.2, "more returns caught, more false alarms"), (0.5, "the model catches almost no returns")]:
    matrix = confusion_matrix(y_test, (proba >= t).astype(int))
    disp = ConfusionMatrixDisplay(matrix, display_labels=["Kept", "Returned"])
    disp.plot(cmap="Blues", colorbar=False)
    plt.title(f"Threshold {t}: {note}")
    save_chart(disp.figure_, f"9_5_confusion_threshold_{str(t).replace('.', '_')}")
