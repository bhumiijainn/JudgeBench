import json
from pathlib import Path


RESULT_DIR = Path("result")

AB_COMPARISON_PATH = (
    RESULT_DIR / "ab_comparison.json"
)


def load_pairwise_results(
    result_dir=RESULT_DIR,
):
    """
    Load completed pairwise result files.
    """

    if not result_dir.exists():
        return {}

    results = {}

    for path in result_dir.glob(
        "*_pairwise.json"
    ):
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
            continue

        if not isinstance(data, dict):
            continue

        case_id = data.get(
            "case_id"
        )

        winner = data.get(
            "final_winner"
        )

        if not case_id:
            continue

        if winner not in {
            "A",
            "B",
            "tie",
        }:
            continue

        results[str(case_id)] = data

    return results


def calculate_ab_comparison(
    results,
    expected_cases=None,
):
    """
    Aggregate pairwise results into an A/B
    comparison.

    A winner means the original candidate A
    won.

    B winner means the original candidate B
    won.

    Ties are not counted as wins.
    """

    total_cases = len(results)

    a_wins = sum(
        1
        for result in results.values()
        if result.get("final_winner") == "A"
    )

    b_wins = sum(
        1
        for result in results.values()
        if result.get("final_winner") == "B"
    )

    ties = sum(
        1
        for result in results.values()
        if result.get("final_winner") == "tie"
    )

    if total_cases:
        a_win_rate = (
            a_wins / total_cases
        )

        b_win_rate = (
            b_wins / total_cases
        )
    else:
        a_win_rate = 0.0
        b_win_rate = 0.0

    if (
        expected_cases is not None
        and total_cases < expected_cases
    ):
        winner = None
        status = "INCOMPLETE"

    elif total_cases == 0:
        winner = None
        status = "INCOMPLETE"

    elif a_wins > b_wins:
        winner = "A"
        status = "COMPLETE"

    elif b_wins > a_wins:
        winner = "B"
        status = "COMPLETE"

    else:
        winner = "tie"
        status = "COMPLETE"

    return {
        "configuration_a": "Candidate A",
        "configuration_b": "Candidate B",
        "comparable_cases": total_cases,
        "expected_cases": expected_cases,
        "a_wins": a_wins,
        "b_wins": b_wins,
        "ties": ties,
        "a_win_rate": round(
            a_win_rate,
            4,
        ),
        "b_win_rate": round(
            b_win_rate,
            4,
        ),
        "winner": winner,
        "status": status,
    }


def build_report(
    results,
    expected_cases=None,
):
    comparison = (
        calculate_ab_comparison(
            results,
            expected_cases=expected_cases,
        )
    )

    return {
        "benchmark": "JudgeBench",
        "comparison_type":
            "pairwise_ab",
        "comparison": comparison,
        "cases": {
            case_id: {
                "final_winner":
                    result.get(
                        "final_winner"
                    ),
                "position_flip":
                    result.get(
                        "position_flip",
                        False,
                    ),
            }
            for case_id, result
            in results.items()
        },
    }


def save_report(
    report,
    path=AB_COMPARISON_PATH,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )


def run_ab_comparison(
    expected_cases=None,
):
    results = load_pairwise_results()

    report = build_report(
        results,
        expected_cases=expected_cases,
    )

    save_report(report)

    comparison = report[
        "comparison"
    ]

    print()
    print(
        "=================================================="
    )
    print(
        "JUDGEBENCH A/B COMPARISON"
    )
    print(
        "=================================================="
    )

    print(
        f"Configuration A: "
        f"{comparison['configuration_a']}"
    )

    print(
        f"Configuration B: "
        f"{comparison['configuration_b']}"
    )

    print(
        f"Comparable cases: "
        f"{comparison['comparable_cases']}"
    )

    if expected_cases is not None:
        print(
            f"Expected cases: "
            f"{expected_cases}"
        )

    print()

    print(
        f"A wins: "
        f"{comparison['a_wins']}"
    )

    print(
        f"B wins: "
        f"{comparison['b_wins']}"
    )

    print(
        f"Ties: "
        f"{comparison['ties']}"
    )

    print()

    print(
        f"A win rate: "
        f"{comparison['a_win_rate']:.2%}"
    )

    print(
        f"B win rate: "
        f"{comparison['b_win_rate']:.2%}"
    )

    print()

    if comparison["winner"] is None:
        print(
            "Winner: NOT DECLARED"
        )

        print(
            "Reason: insufficient "
            "completed cases."
        )

    elif comparison["winner"] == "tie":
        print(
            "Winner: TIE"
        )

    else:
        print(
            f"Winner: "
            f"Configuration "
            f"{comparison['winner']}"
        )

    print()

    print(
        f"Status: "
        f"{comparison['status']}"
    )

    print()

    print(
        "A/B comparison saved to: "
        f"{AB_COMPARISON_PATH}"
    )

    return report


def main():
    run_ab_comparison()


if __name__ == "__main__":
    main()