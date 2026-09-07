"""Train an auditable baseline after replacing the example CSV with verified data."""
import argparse
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = ["district","upazila","crop","ph","nitrogen","phosphorus","potassium","texture","moisture","drainage"]
CATEGORICAL = ["district","upazila","crop","nitrogen","phosphorus","potassium","texture","drainage"]
NUMERIC = ["ph","moisture"]

def train(csv_path: str, output: str):
    data = pd.read_csv(csv_path).dropna(subset=["label","district"])
    missing = set(FEATURES + ["label"]) - set(data.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")
    if len(data) < 200: raise ValueError("Refusing to train: at least 200 verified rows are required.")
    split = GroupShuffleSplit(n_splits=1, test_size=.2, random_state=42)
    train_idx, test_idx = next(split.split(data, groups=data["district"]))
    pre = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL), ("num", "passthrough", NUMERIC)])
    pipe = Pipeline([("preprocess", pre), ("model", RandomForestClassifier(n_estimators=300, class_weight="balanced", random_state=42))])
    pipe.fit(data.iloc[train_idx][FEATURES], data.iloc[train_idx]["label"])
    print(classification_report(data.iloc[test_idx]["label"], pipe.predict(data.iloc[test_idx][FEATURES])))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"version":"soil-risk-v0.1","features":FEATURES,"pipeline":pipe}, output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--output", default="model_artifacts/soil_risk.joblib")
    args = parser.parse_args()
    train(args.csv, args.output)
