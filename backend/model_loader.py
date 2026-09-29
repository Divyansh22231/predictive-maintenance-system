import os
from pathlib import Path
import joblib


def get_project_root() -> Path:
    """
    Locates the project root directory whether running locally or inside Docker.
    """
    # 1. Check current working directory
    current = Path.cwd()
    if (current / "models" / "random_forest.pkl").exists():
        return current
    if (current.parent / "models" / "random_forest.pkl").exists():
        return current.parent

    # 2. Check relative to this file location
    file_dir = Path(__file__).resolve().parent
    if (file_dir.parent / "models" / "random_forest.pkl").exists():
        return file_dir.parent
    if (file_dir / "models" / "random_forest.pkl").exists():
        return file_dir

    return file_dir.parent


_MODEL = None


def load_model():
    """
    Loads the trained Random Forest model once and caches it in memory.
    """
    global _MODEL
    if _MODEL is None:
        root = get_project_root()
        model_path = root / "models" / "random_forest.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {model_path}")
        _MODEL = joblib.load(model_path)
    return _MODEL
