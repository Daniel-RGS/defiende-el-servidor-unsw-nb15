from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_TRAIN = ROOT / "data/raw/UNSW_NB15_training-set.csv"
RAW_TEST = ROOT / "data/raw/UNSW_NB15_testing-set.csv"
SPLITS = ROOT / "data/prepared/split_assignments.csv"
EXPERIMENT_NAME = "defiende-servidor-unsw-nb15"
SEED = 20261027
CATEGORICAL = ["proto", "service", "state"]
EXCLUDED = ["label", "attack_cat", "id"]

