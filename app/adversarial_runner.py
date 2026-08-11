import json
from pathlib import Path

from app.loader import load_test_suite
from app.pairwise import PairwiseJudge


RESULT_DIR = Path("result")
CASE_RESULTS_PATH = (
    RESULT_DIR / "adversarial_cases.json"
)
REPORT_PATH = (
    RESULT_DIR / "adversarial_position_bias.json"
)


def load_completed_results():
    """
    Load previously completed adversarial cases.

    This allows the experiment to resume after:
    - rate limits
    - quota exhaustion
    - network failures
    - interrupted execution
    """

    if not CASE_RESULTS_PATH.exists():
        return {}

    try:
        data = json.loads(
            CASE_RESULTS_PATH.read_text(
                encoding="utf-8"
            )
        )
    except (
        json.JSONDecodeError,
        OSError,
    ):
        return {}

    if not isinstance(data, list):
        return {}

    return {
        item["case_id"]: item
        for item in data
        if isinstance(item, dict)
        and item.get("case_id")
    }


def save_completed_results(results):
    """
    Save completed cases immediately.

    Never wait until the entire experiment finishes.
    """

    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ordered_results = sorted(
        results.values(),
        key=lambda item: item["case_id"],
    )

    CASE_RESULTS_PATH.write_text(
        json.dumps(
            ordered_results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def build_case_result(
    case,
    result,
):
    expected_winner = case.get(
        "expected_winner"
    )

    expected_matches = (
        result.final_winner
        == expected_winner
    )

    return {
        "case_id": case.get("id"),
        "category": case.get(
            "category"
        ),
        "expected_winner": (
            expected_winner
        ),
        "first_order_winner": (
            result.first_order_winner
        ),
        "second_order_winner": (
            result.second_order_winner
        ),
        "final_winner": (
            result.final_winner
        ),
        "position_flip": (
            result.position_flip
        ),
        "expected_winner_match": (
            expected_matches
        ),
        "first_order_reason": (
            result.first_order_reason
        ),
        "second_order_reason": (
            result.second_order_reason
        ),
        "input_tokens": (
            result.first_order_input_tokens
            + result.second_order_input_tokens
        ),
        "output_tokens": (
            result.first_order_output_tokens
            + result.second_order_output_tokens
        ),
        "latency_ms": (
            result.first_order_latency_ms
            + result.second_order_latency_ms
        ),
    }


def build_report(results):
    """
    Build an aggregate report from whatever cases
    have actually completed.

    Incomplete cases are NOT treated as failures.
    """

    ordered_results = sorted(
        results.values(),
        key=lambda item: item["case_id"],
    )

    total_cases = len(
        ordered_results
    )

    flip_count = sum(
        1
        for result in ordered_results
        if result.get("position_flip")
    )

    expected_match_count = sum(
        1
        for result in ordered_results
        if result.get(
            "expected_winner_match"
        )
    )

    position_flip_rate = (
        flip_count / total_cases
        if total_cases
        else 0.0
    )

    expected_winner_accuracy = (
        expected_match_count / total_cases
        if total_cases
        else 0.0
    )

    total_input_tokens = sum(
        result.get(
            "input_tokens",
            0,
        )
        for result in ordered_results
    )

    total_output_tokens = sum(
        result.get(
            "output_tokens",
            0,
        )
        for result in ordered_results
    )

    total_latency_ms = sum(
        result.get(
            "latency_ms",
            0,
        )
        for result in ordered_results
    )

    report = {
        "experiment": (
            "adversarial_position_bias"
        ),
        "completed_cases": (
            total_cases
        ),
        "position_flips": flip_count,
        "position_flip_rate": (
            position_flip_rate
        ),
        "expected_winner_matches": (
            expected_match_count
        ),
        "expected_winner_accuracy": (
            expected_winner_accuracy
        ),
        "total_input_tokens": (
            total_input_tokens
        ),
        "total_output_tokens": (
            total_output_tokens
        ),
        "total_latency_ms": (
            total_latency_ms
        ),
        "cases": ordered_results,
    }

    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return report


def print_report(
    report,
    total_dataset_cases,
):
    completed_cases = report[
        "completed_cases"
    ]

    print("\n")
    print("=" * 55)
    print(
        "ADVERSARIAL POSITION-BIAS REPORT"
    )
    print("=" * 55)

    print(
        f"Completed cases: "
        f"{completed_cases}/{total_dataset_cases}"
    )

    print(
        f"Position flips: "
        f"{report['position_flips']}"
    )

    print(
        f"Position flip rate: "
        f"{report['position_flip_rate']:.2%}"
    )

    print(
        f"Expected winner matches: "
        f"{report['expected_winner_matches']}"
        f"/{completed_cases}"
    )

    if completed_cases:
        print(
            f"Expected-winner accuracy: "
            f"{report['expected_winner_accuracy']:.2%}"
        )
    else:
        print(
            "Expected-winner accuracy: N/A"
        )

    print(
        f"Total input tokens: "
        f"{report['total_input_tokens']}"
    )

    print(
        f"Total output tokens: "
        f"{report['total_output_tokens']}"
    )

    print(
        f"Total latency: "
        f"{report['total_latency_ms']:.2f} ms"
    )

    if completed_cases < total_dataset_cases:
        print()
        print(
            "STATUS: INCOMPLETE"
        )

        print(
            f"{total_dataset_cases - completed_cases} "
            "case(s) still need evaluation."
        )

    else:
        print()
        print(
            "STATUS: COMPLETE"
        )

    print()
    print(
        "Case results saved:"
    )
    print(
        CASE_RESULTS_PATH
    )

    print(
        "\nAggregate report saved:"
    )
    print(
        REPORT_PATH
    )


def is_rate_limit_error(exc):
    """
    Detect common Gemini quota/rate-limit errors
    without depending on a specific SDK exception class.
    """

    error_text = str(exc).lower()

    indicators = [
        "429",
        "quota",
        "rate limit",
        "rate_limit",
        "too_many_requests",
        "free_tier",
    ]

    return any(
        indicator in error_text
        for indicator in indicators
    )


def run_adversarial_suite():
    cases = load_test_suite(
        "data/adversarial.yaml"
    )

    if not cases:
        print(
            "No adversarial cases found."
        )
        return

    completed = load_completed_results()

    total_cases = len(cases)

    already_completed = sum(
        1
        for case in cases
        if case.get("id") in completed
    )

    if already_completed:
        print(
            f"Resuming experiment: "
            f"{already_completed}/{total_cases} "
            "cases already completed."
        )

    judge = PairwiseJudge()

    interrupted_by_quota = False

    for index, case in enumerate(
        cases,
        start=1,
    ):
        case_id = case.get("id")

        if case_id in completed:
            print(
                f"\n[{index}/{total_cases}] "
                f"{case_id}"
            )

            print(
                "Already completed — skipping."
            )

            continue

        candidate_a = case.get(
            "candidate_a",
            {},
        )

        candidate_b = case.get(
            "candidate_b",
            {},
        )

        output_a = candidate_a.get(
            "output",
            "",
        )

        output_b = candidate_b.get(
            "output",
            "",
        )

        print(
            f"\n[{index}/{total_cases}] "
            f"{case_id}"
        )

        print(
            "Running A-first and B-first..."
        )

        try:
            result = judge.evaluate(
                case_id=case_id,
                user_input=case.get(
                    "input",
                    "",
                ),
                system_prompt=case.get(
                    "system_prompt",
                    "",
                ),
                candidate_a=output_a,
                candidate_b=output_b,
            )

        except Exception as exc:
            print()
            print(
                "Evaluation stopped."
            )

            if is_rate_limit_error(exc):
                print(
                    "Reason: Gemini rate limit/quota "
                    "was reached."
                )

                print(
                    "Completed results have already "
                    "been saved."
                )

                print(
                    "Wait for the quota window to reset "
                    "and run the same command again."
                )

                interrupted_by_quota = True

            else:
                print(
                    f"Error: {exc}"
                )

                print(
                    "Completed results have already "
                    "been saved."
                )

            break

        case_result = build_case_result(
            case,
            result,
        )

        completed[case_id] = (
            case_result
        )

        # Save immediately after EVERY
        # successful case.
        save_completed_results(
            completed
        )

        print(
            f"  Expected: "
            f"{case_result['expected_winner']}"
        )

        print(
            f"  A-first: "
            f"{case_result['first_order_winner']}"
        )

        print(
            f"  B-first: "
            f"{case_result['second_order_winner']}"
        )

        print(
            f"  Final: "
            f"{case_result['final_winner']}"
        )

        print(
            f"  Position flip: "
            f"{'YES' if case_result['position_flip'] else 'NO'}"
        )

        print(
            f"  Expected match: "
            f"{'YES' if case_result['expected_winner_match'] else 'NO'}"
        )

        print(
            "  Saved immediately."
        )

    report = build_report(
        completed
    )

    print_report(
        report,
        total_cases,
    )

    if interrupted_by_quota:
        print()
        print(
            "RESUME COMMAND:"
        )
        print(
            "python main.py run-adversarial"
        )