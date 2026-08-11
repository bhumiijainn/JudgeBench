import json
from pathlib import Path
from typing import Any


RESULT_DIR = Path("result")

TEST_RETEST_RESULT_PATH = (
    RESULT_DIR / "test_retest.json"
)

DEFAULT_REPETITIONS = 2


def load_test_cases():
    from app.loader import load_test_suite

    return load_test_suite(
        "data/test_suite.yaml"
    )


def _candidate_text(candidate):
    if isinstance(candidate, dict):
        return candidate.get(
            "output",
            "",
        )

    return str(candidate or "")


def _result_to_dict(result):
    if hasattr(
        result,
        "model_dump",
    ):
        return result.model_dump()

    if hasattr(
        result,
        "dict",
    ):
        return result.dict()

    if isinstance(result, dict):
        return result

    raise TypeError(
        "Unsupported pairwise result type."
    )


def run_single_evaluation(case):
    """
    Run one pairwise evaluation for a case.
    """

    from app.pairwise import (
        PairwiseJudge,
    )

    candidate_a = _candidate_text(
        case.get("candidate_a")
    )

    candidate_b = _candidate_text(
        case.get("candidate_b")
    )

    judge = PairwiseJudge()

    result = judge.evaluate(
        case_id=str(
            case["id"]
        ),
        user_input=str(
            case.get(
                "input",
                "",
            )
        ),
        system_prompt=str(
            case.get(
                "system_prompt",
                "",
            )
        ),
        candidate_a=candidate_a,
        candidate_b=candidate_b,
    )

    return _result_to_dict(
        result
    )


def load_existing_results(
    path=TEST_RETEST_RESULT_PATH,
):
    """
    Load previously completed test-retest
    results so interrupted runs can resume.
    """

    if not path.exists():
        return {}

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )
    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}

    if not isinstance(data, dict):
        return {}

    results = data.get(
        "cases",
        {},
    )

    if not isinstance(
        results,
        dict,
    ):
        return {}

    return results


def save_results(
    results,
    path=TEST_RETEST_RESULT_PATH,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = {
        "benchmark": "JudgeBench",
        "validation_type":
            "test_retest_consistency",
        "repetitions":
            DEFAULT_REPETITIONS,
        "cases": results,
    }

    path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )


def evaluate_case_repeatedly(
    case,
    repetitions=DEFAULT_REPETITIONS,
):
    """
    Run the exact same case multiple times.
    """

    runs = []

    for run_number in range(
        1,
        repetitions + 1,
    ):
        result = run_single_evaluation(
            case
        )

        runs.append(
            {
                "run":
                    run_number,
                "final_winner":
                    result.get(
                        "final_winner"
                    ),
                "position_flip":
                    result.get(
                        "position_flip"
                    ),
                "first_order_winner":
                    result.get(
                        "first_order_winner"
                    ),
                "second_order_winner":
                    result.get(
                        "second_order_winner"
                    ),
                "first_order_reason":
                    result.get(
                        "first_order_reason"
                    ),
                "second_order_reason":
                    result.get(
                        "second_order_reason"
                    ),
                "metrics": result.get(
                    "metrics",
                    {},
                ),
            }
        )

    winners = [
        run["final_winner"]
        for run in runs
    ]

    consistent = (
        len(set(winners)) == 1
    )

    return {
        "case_id":
            case["id"],
        "runs":
            runs,
        "final_winners":
            winners,
        "consistent":
            consistent,
        "verdict_flip":
            not consistent,
    }


def calculate_consistency(
    case_results,
):
    """
    Calculate test-retest consistency
    across completed cases.
    """

    total_cases = len(
        case_results
    )

    if total_cases == 0:
        return {
            "completed_cases": 0,
            "consistent_cases": 0,
            "flipped_cases": 0,
            "consistency_rate": 0.0,
            "flip_rate": 0.0,
        }

    consistent_cases = sum(
        1
        for result in case_results
        if result.get(
            "consistent",
            False,
        )
    )

    flipped_cases = (
        total_cases
        - consistent_cases
    )

    consistency_rate = (
        consistent_cases
        / total_cases
    )

    flip_rate = (
        flipped_cases
        / total_cases
    )

    return {
        "completed_cases":
            total_cases,
        "consistent_cases":
            consistent_cases,
        "flipped_cases":
            flipped_cases,
        "consistency_rate":
            round(
                consistency_rate,
                4,
            ),
        "consistency_percent":
            round(
                consistency_rate * 100,
                2,
            ),
        "flip_rate":
            round(
                flip_rate,
                4,
            ),
        "flip_percent":
            round(
                flip_rate * 100,
                2,
            ),
    }


def build_report(
    case_results,
    expected_cases,
):
    metrics = calculate_consistency(
        case_results
    )

    return {
        "benchmark": "JudgeBench",
        "validation_type":
            "test_retest_consistency",
        "repetitions":
            DEFAULT_REPETITIONS,
        "expected_cases":
            expected_cases,
        "metrics":
            metrics,
        "status": (
            "COMPLETE"
            if metrics[
                "completed_cases"
            ] == expected_cases
            else "INCOMPLETE"
        ),
        "cases": {
            result["case_id"]:
                result
            for result in case_results
        },
    }


def run_test_retest(
    repetitions=DEFAULT_REPETITIONS,
    max_cases=None,
):
    cases = load_test_cases()

    if max_cases is not None:
        cases = cases[
            :max_cases
        ]

    existing = (
        load_existing_results()
    )

    print()
    print(
        "=================================================="
    )
    print(
        "JUDGEBENCH TEST-RETEST CONSISTENCY"
    )
    print(
        "=================================================="
    )

    print(
        f"Cases requested: "
        f"{len(cases)}"
    )

    print(
        f"Repetitions per case: "
        f"{repetitions}"
    )

    completed = {}

    for case in cases:
        case_id = str(
            case["id"]
        )

        if case_id in existing:
            completed[
                case_id
            ] = existing[
                case_id
            ]

            print(
                f"[SKIP] "
                f"{case_id} "
                f"(already completed)"
            )

            continue

        print()
        print(
            f"[RUN] {case_id}"
        )

        try:
            result = (
                evaluate_case_repeatedly(
                    case,
                    repetitions=repetitions,
                )
            )

            completed[
                case_id
            ] = result

            save_results(
                completed
            )

            print(
                f"  Winners: "
                f"{result['final_winners']}"
            )

            print(
                f"  Consistent: "
                f"{'YES' if result['consistent'] else 'NO'}"
            )

        except Exception as exc:
            print(
                f"  FAILED: {exc}"
            )

            save_results(
                completed
            )

    case_results = list(
        completed.values()
    )

    report = build_report(
        case_results,
        expected_cases=len(cases),
    )

    save_results(
        completed
    )

    print()
    print(
        "=================================================="
    )
    print(
        "TEST-RETEST SUMMARY"
    )
    print(
        "=================================================="
    )

    metrics = report[
        "metrics"
    ]

    print(
        f"Completed cases: "
        f"{metrics['completed_cases']}/"
        f"{report['expected_cases']}"
    )

    print(
        f"Consistent cases: "
        f"{metrics['consistent_cases']}"
    )

    print(
        f"Verdict flips: "
        f"{metrics['flipped_cases']}"
    )

    print(
        f"Consistency rate: "
        f"{metrics['consistency_percent']:.2f}%"
    )

    print(
        f"Flip rate: "
        f"{metrics['flip_percent']:.2f}%"
    )

    print()
    print(
        f"Status: "
        f"{report['status']}"
    )

    print()
    print(
        "Report saved to: "
        f"{TEST_RETEST_RESULT_PATH}"
    )

    return report


def main():
    run_test_retest()


if __name__ == "__main__":
    main()