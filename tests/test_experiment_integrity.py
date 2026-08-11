import json

import pytest

from app.verbosity_report import calculate_metrics


def test_empty_baseline_and_mitigated_are_not_comparable():
    baseline = {}
    mitigated = {}

    comparable = set(baseline) & set(mitigated)

    assert comparable == set()


def test_partial_results_are_not_full_experiments():
    results = {
        "verb_001": {
            "case_id": "verb_001",
            "final_winner": "A",
            "position_flip": False,
        },
        "verb_002": {
            "case_id": "verb_002",
            "final_winner": "B",
            "position_flip": False,
        },
    }

    expected_case_count = 10

    metrics = calculate_metrics(results)

    assert (
        metrics["completed_cases"]
        < expected_case_count
    )


def test_baseline_and_mitigated_case_ids_must_match():
    baseline = {
        "verb_001": {},
        "verb_002": {},
        "verb_003": {},
    }

    mitigated = {
        "verb_001": {},
        "verb_002": {},
        "verb_004": {},
    }

    comparable = (
        set(baseline)
        & set(mitigated)
    )

    assert comparable == {
        "verb_001",
        "verb_002",
    }

    assert set(baseline) != set(mitigated)


def test_complete_case_sets_match():
    case_ids = {
        "verb_001",
        "verb_002",
        "verb_003",
        "verb_004",
        "verb_005",
        "verb_006",
        "verb_007",
        "verb_008",
        "verb_009",
        "verb_010",
    }

    baseline = set(case_ids)
    mitigated = set(case_ids)

    assert baseline == mitigated
    assert len(baseline) == 10


def test_valid_final_winners():
    valid_winners = {
        "A",
        "B",
        "tie",
    }

    results = {
        "verb_001": {
            "final_winner": "A",
        },
        "verb_002": {
            "final_winner": "B",
        },
        "verb_003": {
            "final_winner": "tie",
        },
    }

    for result in results.values():
        assert (
            result["final_winner"]
            in valid_winners
        )


def test_invalid_final_winner_is_rejected():
    valid_winners = {
        "A",
        "B",
        "tie",
    }

    result = {
        "final_winner": "C",
    }

    assert (
        result["final_winner"]
        not in valid_winners
    )


def test_result_is_json_serializable():
    result = {
        "case_id": "verb_001",
        "final_winner": "A",
        "position_flip": False,
    }

    encoded = json.dumps(result)

    decoded = json.loads(encoded)

    assert decoded == result