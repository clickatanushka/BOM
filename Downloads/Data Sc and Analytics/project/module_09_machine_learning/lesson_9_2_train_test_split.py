"""Video 9.2 - The ML workflow and train/test split
Run: python module_09_machine_learning/lesson_9_2_train_test_split.py"""

import pandas as pd
from sklearn.model_selection import train_test_split

from module_06_pandas_eda.cleaning import load_clean
from module_09_machine_learning.models import LESSON_FEATURES

# The workflow we follow in every ML video:
#   1. ask a question  2. choose y and X  3. split train/test
#   4. train (fit)  5. predict on test  6. evaluate
df = load_clean()
print(df.shape)

print("\n== Step 2 - target (y) and features (X) ==")
y = (df["returned"] == "Y").astype(int)     # models need numbers, not "Y"/"N"
print(y.value_counts())
print("Share returned:", round(y.mean() * 100, 1), "%")

X_raw = df[LESSON_FEATURES]
print(X_raw.head().to_string())

print("\n== Models only understand numbers: one-hot encoding ==")
print(pd.get_dummies(df[["category"]].head(5), dtype=int))

# drop_first=True drops one column per group - it is redundant
X = pd.get_dummies(X_raw, drop_first=True, dtype=int)
print("Columns before:", X_raw.shape[1], " after:", X.shape[1])
print(list(X.columns))

print("\n== Step 3 - split into train and test ==")
# random_state=42 -> same split every time; stratify=y -> same share of returns (~14%) in train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
print("Train rows:", len(X_train), " Test rows:", len(X_test))
print("Return share in train:", round(y_train.mean() * 100, 2), "%")
print("Return share in test :", round(y_test.mean() * 100, 2), "%")

print("\n== Bonus: why random_state matters ==")
for seed in [1, 42, 7]:
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=seed)
    print("random_state =", seed, "-> first 5 test row numbers:", list(X_test.index[:5]))
