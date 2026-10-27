import pandas as pd
from sklearn.linear_model import LogisticRegression
from src.config import EXCLUDED
from src.pipeline import make_pipeline_from_frame

def test_excluded_columns_are_not_model_inputs():
    X = pd.DataFrame({"proto":["tcp"], "service":["-"], "state":["FIN"], "dur":[1.0]})
    model = make_pipeline_from_frame(X, LogisticRegression(max_iter=100))
    assert not (set(EXCLUDED) & set(X.columns))
    assert set(model.named_steps["preprocessor"].transformers[0][2] + model.named_steps["preprocessor"].transformers[1][2]).isdisjoint(EXCLUDED)

