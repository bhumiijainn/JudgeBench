from app.ab_comparison import (
    calculate_ab_comparison,
    build_report,
)


def test_a_wins_majority():
    results = {
        "case_001": {
            "final_winner": "A",
        },
        "case_002": {
            "final_winner": "A",
        },
        "case_003": {
            "final_winner": "B",
        },
        "case_004": {
            "final_winner": "tie",
        },
    }

    result = calculate_ab_comparison(
        results,
        expected_cases=4,
    )

    assert result[
        "a_wins"
    ] == 2

    assert result[
        "b_wins"
    ] == 1

    assert result[
        "ties"
    ] == 1

    assert result[
        "winner"
    ] == "A"

    assert result[
        "status"
    ] == "COMPLETE"


def test_b_wins_majority():
    results = {
        "case_001": {
            "final_winner": "B",
        },
        "case_002": {
            "final_winner": "B",
        },
        "case_003": {
            "final_winner": "A",
        },
    }

    result = calculate_ab_comparison(
        results,
        expected_cases=3,
    )

    assert result[
        "a_wins"
    ] == 1

    assert result[
        "b_wins"
    ] == 2

    assert result[
        "winner"
    ] == "B"


def test_tie_is_declared_when_wins_equal():
    results = {
        "case_001": {
            "final_winner": "A",
        },
        "case_002": {
            "final_winner": "B",
        },
    }

    result = calculate_ab_comparison(
        results,
        expected_cases=2,
    )

    assert result[
        "winner"
    ] == "tie"

    assert result[
        "status"
    ] == "COMPLETE"


def test_incomplete_results_do_not_declare_winner():
    results = {
        "case_001": {
            "final_winner": "A",
        },
        "case_002": {
            "final_winner": "B",
        },
    }

    result = calculate_ab_comparison(
        results,
        expected_cases=10,
    )

    assert result[
        "winner"
    ] is None

    assert result[
        "status"
    ] == "INCOMPLETE"


def test_empty_results_are_incomplete():
    result = calculate_ab_comparison(
        {},
        expected_cases=10,
    )

    assert result[
        "comparable_cases"
    ] == 0

    assert result[
        "winner"
    ] is None

    assert result[
        "status"
    ] == "INCOMPLETE"


def test_win_rates_are_calculated():
    results = {
        "case_001": {
            "final_winner": "A",
        },
        "case_002": {
            "final_winner": "A",
        },
        "case_003": {
            "final_winner": "B",
        },
        "case_004": {
            "final_winner": "tie",
        },
    }

    result = calculate_ab_comparison(
        results,
        expected_cases=4,
    )

    assert result[
        "a_win_rate"
    ] == 0.5

    assert result[
        "b_win_rate"
    ] == 0.25


def test_build_report_contains_case_results():
    results = {
        "qa_001": {
            "final_winner": "A",
            "position_flip": False,
        }
    }

    report = build_report(
        results,
        expected_cases=1,
    )

    assert (
        report["benchmark"]
        == "JudgeBench"
    )

    assert (
        report["comparison_type"]
        == "pairwise_ab"
    )

    assert (
        report["comparison"]["winner"]
        == "A"
    )

    assert (
        "qa_001"
        in report["cases"]
    )