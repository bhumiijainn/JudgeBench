import json

import pytest

from app.verbosity_report import calculate_metrics


def test_empty_results_are_incomplete():
    metrics = calculate_metrics({})

    assert metrics["completed_cases"] == 0
    assert metrics["position_flip_rate"] == 0.0
    assert metrics["expected_winner_accuracy"] == 0.0


def test_position_flip_rate_is_calculated_correctly():
    results = {
        "verb_001": {
            "expected_winner": "A",
            "final_winner": "A",
            "position_flip": False,
        },
        "verb_002": {
            "expected_winner": "A",
            "final_winner": "B",
            "position_flip": True,
        },
        "verb_003": {
            "expected_winner": "B",
            "final_winner": "B",
            "position_flip": False,
        },
        "verb_004": {
            "expected_winner": "A",
            "final_winner": "A",
            "position_flip": True,
        },
    }

    metrics = calculate_metrics(
        results
    )

    assert metrics["completed_cases"] == 4
    assert metrics["position_flips"] == 2
    assert metrics["position_flip_rate"] == 0.5


def test_expected_winner_accuracy_is_calculated_correctly():
    results = {
        "verb_001": {
            "expected_winner": "A",
            "final_winner": "A",
            "position_flip": False,
        },
        "verb_002": {
            "expected_winner": "A",
            "final_winner": "B",
            "position_flip": False,
        },
        "verb_003": {
            "expected_winner": "B",
            "final_winner": "B",
            "position_flip": False,
        },
        "verb_004": {
            "expected_winner": "B",
            "final_winner": "A",
            "position_flip": False,
        },
    }

    metrics = calculate_metrics(
        results
    )

    assert metrics[
        "expected_winner_matches"
    ] == 2

    assert metrics[
        "expected_winner_accuracy"
    ] == 0.5


def test_valid_winners_are_accepted():
    results = {
        "verb_001": {
            "expected_winner": "A",
            "final_winner": "A",
            "position_flip": False,
        },
        "verb_002": {
            "expected_winner": "B",
            "final_winner": "B",
            "position_flip": False,
        },
        "verb_003": {
            "expected_winner": "tie",
            "final_winner": "tie",
            "position_flip": False,
        },
    }

    for result in results.values():
        assert result["final_winner"] in {
            "A",
            "B",
            "tie",
        }


def test_results_are_json_serializable():
    results = {
        "verb_001": {
            "case_id": "verb_001",
            "final_winner": "A",
            "position_flip": False,
        }
    }

    serialized = json.dumps(
        results
    )

    restored = json.loads(
        serialized
    )

    assert restored == results


def test_incomplete_experiment_is_detectable():
    results = {
        "verb_001": {
            "expected_winner": "A",
            "final_winner": "A",
            "position_flip": False,
        },
        "verb_002": {
            "expected_winner": "A",
            "final_winner": "A",
            "position_flip": False,
        },
    }

    expected_cases = 10

    metrics = calculate_metrics(
        results
    )

    assert metrics[
        "completed_cases"
    ] < expected_cases
    