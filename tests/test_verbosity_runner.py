from pathlib import Path

from app.verbosity_runner import (
    _load_completed,
    _result_path,
    _save_results,
)


def test_result_paths_are_separate():
    baseline = _result_path("baseline")
    mitigated = _result_path("mitigated")

    assert baseline != mitigated
    assert baseline.name == "verbosity_cases.json"
    assert mitigated.name == "verbosity_cases.json"

    assert "baseline" in str(baseline)
    assert "mitigated" in str(mitigated)


def test_save_and_load_completed_results(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.verbosity_runner.BASELINE_DIR",
        tmp_path / "baseline",
    )

    monkeypatch.setattr(
        "app.verbosity_runner.MITIGATED_DIR",
        tmp_path / "mitigated",
    )

    results = {
        "verb_001": {
            "case_id": "verb_001",
            "final_winner": "A",
            "position_flip": False,
        }
    }

    _save_results(
        "baseline",
        results,
    )

    loaded = _load_completed(
        "baseline"
    )

    assert "verb_001" in loaded
    assert (
        loaded["verb_001"]["final_winner"]
        == "A"
    )


def test_baseline_and_mitigated_storage_are_independent(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(
        "app.verbosity_runner.BASELINE_DIR",
        tmp_path / "baseline",
    )

    monkeypatch.setattr(
        "app.verbosity_runner.MITIGATED_DIR",
        tmp_path / "mitigated",
    )

    baseline_results = {
        "verb_001": {
            "case_id": "verb_001",
            "final_winner": "B",
        }
    }

    mitigated_results = {
        "verb_001": {
            "case_id": "verb_001",
            "final_winner": "A",
        }
    }

    _save_results(
        "baseline",
        baseline_results,
    )

    _save_results(
        "mitigated",
        mitigated_results,
    )

    loaded_baseline = _load_completed(
        "baseline"
    )

    loaded_mitigated = _load_completed(
        "mitigated"
    )

    assert (
        loaded_baseline["verb_001"]["final_winner"]
        == "B"
    )

    assert (
        loaded_mitigated["verb_001"]["final_winner"]
        == "A"
    )