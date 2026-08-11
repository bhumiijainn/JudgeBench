from pathlib import Path

import yaml


def load_yaml(path: str | Path) -> dict:
    """Load a YAML file and return its contents."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict):
        raise ValueError("Dataset root must be a YAML object.")

    return data


def load_test_suite(path: str | Path) -> list[dict]:
    """Load and validate the cases section of a test suite."""
    data = load_yaml(path)

    cases = data.get("cases")

    if not isinstance(cases, list):
        raise ValueError("Test suite must contain a 'cases' list.")

    return cases