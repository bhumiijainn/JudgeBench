from app.test_retest import (
    calculate_consistency,
    build_report,
)


def test_all_cases_consistent():
    results = [
        {
            "case_id": "qa_001",
            "consistent": True,
        },
        {
            "case_id": "qa_002",
            "consistent": True,
        },
        {
            "case_id": "qa_003",
            "consistent": True,
        },
    ]

    metrics = calculate_consistency(
        results
    )

    assert metrics[
        "completed_cases"
    ] == 3

    assert metrics[
        "consistent_cases"
    ] == 3

    assert metrics[
        "flipped_cases"
    ] == 0

    assert metrics[
        "consistency_rate"
    ] == 1.0

    assert metrics[
        "flip_rate"
    ] == 0.0


def test_one_case_flips():
    results = [
        {
            "case_id": "qa_001",
            "consistent": True,
        },
        {
            "case_id": "qa_002",
            "consistent": False,
        },
        {
            "case_id": "qa_003",
            "consistent": True,
        },
        {
            "case_id": "qa_004",
            "consistent": True,
        },
    ]

    metrics = calculate_consistency(
        results
    )

    assert metrics[
        "completed_cases"
    ] == 4

    assert metrics[
        "consistent_cases"
    ] == 3

    assert metrics[
        "flipped_cases"
    ] == 1

    assert metrics[
        "consistency_rate"
    ] == 0.75

    assert metrics[
        "flip_rate"
    ] == 0.25


def test_empty_results():
    metrics = calculate_consistency(
        []
    )

    assert metrics[
        "completed_cases"
    ] == 0

    assert metrics[
        "consistent_cases"
    ] == 0

    assert metrics[
        "flipped_cases"
    ] == 0

    assert metrics[
        "consistency_rate"
    ] == 0.0


def test_build_report_is_incomplete():
    results = [
        {
            "case_id": "qa_001",
            "consistent": True,
        }
    ]

    report = build_report(
        results,
        expected_cases=3,
    )

    assert report[
        "status"
    ] == "INCOMPLETE"

    assert report[
        "metrics"
    ][
        "completed_cases"
    ] == 1


def test_build_report_is_complete():
    results = [
        {
            "case_id": "qa_001",
            "consistent": True,
        },
        {
            "case_id": "qa_002",
            "consistent": False,
        },
    ]

    report = build_report(
        results,
        expected_cases=2,
    )

    assert report[
        "status"
    ] == "COMPLETE"

    assert report[
        "metrics"
    ][
        "completed_cases"
    ] == 2

    assert report[
        "metrics"
    ][
        "flipped_cases"
    ] == 1