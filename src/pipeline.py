from joblib import dump, load
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import CATEGORICAL, EXCLUDED

def make_pipeline(X_train, estimator):
    """Un único objeto: preprocesamiento + estimador; fit solo recibe train."""
    return make_pipeline_from_frame(X_train, estimator)

def make_pipeline_from_frame(X_train, estimator):
    numeric = [c for c in X_train.columns if c not in CATEGORICAL]
    forbidden = set(EXCLUDED) & set(X_train.columns)
    if forbidden:
        raise ValueError(f"Columnas excluidas presentes en X: {sorted(forbidden)}")
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL),
    ], remainder="drop")
    return Pipeline([("preprocessor", preprocessor), ("estimator", estimator)])

def save_pipeline(model, path): dump(model, path)
def load_pipeline(path): return load(path)

