"""Module 9 - the ShopKart machine-learning steps as functions.
Reused by the Module 9 lessons and by Module 10 (capstone.py, practice_solutions.py)."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from project_paths import module_output

# Videos 9.2 and 9.4-9.6: what we know when the order ships
LESSON_FEATURES = ["category", "city", "payment_mode", "delivery_days", "discount", "membership", "age", "unit_price"]

# Module 10 capstone. No `rating`: the customer rates AFTER delivery, often while returning
# the item, so it does not exist when we predict. Using it would be data leakage.
RETURN_FEATURES = ["category", "city", "payment_mode", "delivery_days", "discount", "membership"]


def return_features(df, features=RETURN_FEATURES):
    """X (one-hot encoded features) and y (1 = returned) for 'will this order be returned?'."""
    X = pd.get_dummies(df[features], drop_first=True, dtype=int)
    return X, (df["returned"] == "Y").astype(int)


def split(X, y):
    """80/20 split, same every run. stratify keeps the same return share in train and test."""
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def return_models():
    """The capstone's two (unfitted) models. class_weight='balanced' takes the rare returns seriously."""
    return {
        "Decision tree (depth 4)": DecisionTreeClassifier(max_depth=4, class_weight="balanced", random_state=42),
        "Logistic regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    }


def evaluate_classifier(model, X_test, y_test):
    """Accuracy, precision, recall and confusion matrix of a fitted model."""
    pred = model.predict(X_test)
    return {"accuracy": accuracy_score(y_test, pred),
            "precision": precision_score(y_test, pred, zero_division=0),
            "recall": recall_score(y_test, pred, zero_division=0),
            "confusion_matrix": confusion_matrix(y_test, pred)}


def baseline_accuracy(y_test):
    """Accuracy of a 'model' that always says 'not returned' (it catches zero returns)."""
    return (np.asarray(y_test) == 0).mean()


def flagging_summary(model, X_test, y_test):
    """How many orders the model flags, and how often flagged vs not-flagged orders come back."""
    flagged = model.predict(X_test) == 1
    y = np.asarray(y_test)
    return {"flagged": int(flagged.sum()), "orders": len(y), "flagged_share": flagged.mean(),
            "return_rate_flagged": y[flagged].mean(), "return_rate_not_flagged": y[~flagged].mean()}


def save_chart(fig, name):
    """Save a chart to outputs/module_09/<name>.png and show it."""
    fig.savefig(module_output("module_09") / f"{name}.png", dpi=150, bbox_inches="tight")
    if plt.get_backend().lower() != "agg":     # no window in tests (MPLBACKEND=Agg)
        plt.show()
    plt.close(fig)
