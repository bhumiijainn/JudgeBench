import json
from pathlib import Path


RESULT_DIR = Path("result")

BASELINE_FILE = (
    RESULT_DIR
    / "baseline"
    / "verbosity_cases.json"
)

MITIGATED_FILE = (
    RESULT_DIR
    / "mitigated"
    / "verbosity_cases.json"
)

REPORT_FILE = (
    RESULT_DIR
    / "verbosity_report.json"
)

EXPECTED_CASE_COUNT = 10


# ==========================================================
# LOAD RESULTS
# ==========================================================

def load_results(path):
    """
    Load saved verbosity results.

    Missing result files are treated as empty results so
    the report can correctly show INCOMPLETE instead of
    crashing.
    """

    if not path.exists():
        return {}

    data = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if isinstance(data, dict):
        return data

    if isinstance(data, list):
        return {
            item["case_id"]: item
            for item in data
            if "case_id" in item
        }

    raise ValueError(
        f"Unsupported result format: {path}"
    )


# ==========================================================
# METRICS
# ==========================================================

def calculate_metrics(results):
    total = len(results)

    if total == 0:
        return {
            "completed_cases": 0,
            "position_flips": 0,
            "position_flip_rate": 0.0,
            "expected_winner_matches": 0,
            "expected_winner_accuracy": 0.0,
        }

    position_flips = sum(
        1
        for result in results.values()
        if result.get(
            "position_flip"
        ) is True
    )

    expected_matches = sum(
        1
        for result in results.values()
        if (
            result.get(
                "expected_winner"
            )
            and result.get(
                "final_winner"
            )
            == result.get(
                "expected_winner"
            )
        )
    )

    return {
        "completed_cases": total,
        "position_flips": position_flips,
        "position_flip_rate": round(
            position_flips / total,
            4,
        ),
        "expected_winner_matches": expected_matches,
        "expected_winner_accuracy": round(
            expected_matches / total,
            4,
        ),
    }


# ==========================================================
# BUILD REPORT
# ==========================================================

def build_report():
    baseline = load_results(
        BASELINE_FILE
    )

    mitigated = load_results(
        MITIGATED_FILE
    )

    baseline_metrics = calculate_metrics(
        baseline
    )

    mitigated_metrics = calculate_metrics(
        mitigated
    )

    baseline_ids = set(
        baseline.keys()
    )

    mitigated_ids = set(
        mitigated.keys()
    )

    comparable_ids = sorted(
        baseline_ids
        & mitigated_ids
    )

    complete_baseline = (
        len(baseline)
        == EXPECTED_CASE_COUNT
    )

    complete_mitigated = (
        len(mitigated)
        == EXPECTED_CASE_COUNT
    )

    matching_case_sets = (
        baseline_ids
        == mitigated_ids
    )

    complete_comparison = (
        complete_baseline
        and complete_mitigated
        and matching_case_sets
    )

    winner_changes = 0

    for case_id in comparable_ids:
        baseline_winner = baseline[
            case_id
        ].get(
            "final_winner"
        )

        mitigated_winner = mitigated[
            case_id
        ].get(
            "final_winner"
        )

        if (
            baseline_winner
            != mitigated_winner
        ):
            winner_changes += 1

    if comparable_ids:
        winner_change_rate = (
            winner_changes
            / len(comparable_ids)
        )
    else:
        winner_change_rate = 0.0

    status = (
        "COMPLETE"
        if complete_comparison
        else "INCOMPLETE"
    )

    report = {
        "experiment": (
            "verbosity_mitigation"
        ),
        "status": status,

        "expected_case_count":
            EXPECTED_CASE_COUNT,

        "baseline_completed":
            len(baseline),

        "mitigated_completed":
            len(mitigated),

        "complete_baseline":
            complete_baseline,

        "complete_mitigated":
            complete_mitigated,

        "matching_case_sets":
            matching_case_sets,

        "comparable_cases":
            len(comparable_ids),

        "winner_changes":
            winner_changes,

        "winner_change_rate":
            round(
                winner_change_rate,
                4,
            ),

        "baseline":
            baseline_metrics,

        "mitigated":
            mitigated_metrics,

        "cases": {
            case_id: {
                "baseline_winner":
                    baseline[
                        case_id
                    ].get(
                        "final_winner"
                    ),

                "mitigated_winner":
                    mitigated[
                        case_id
                    ].get(
                        "final_winner"
                    ),

                "baseline_position_flip":
                    baseline[
                        case_id
                    ].get(
                        "position_flip"
                    ),

                "mitigated_position_flip":
                    mitigated[
                        case_id
                    ].get(
                        "position_flip"
                    ),
            }
            for case_id in comparable_ids
        },
    }

    return report


# ==========================================================
# SAVE REPORT
# ==========================================================

def save_report(report):
    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )


# ==========================================================
# PRINT REPORT
# ==========================================================

def print_report(report):
    print()
    print(
        "========================================"
    )
    print(
        "VERBOSITY EXPERIMENT REPORT"
    )
    print(
        "========================================"
    )

    print(
        f"Status: "
        f"{report['status']}"
    )

    print(
        f"Baseline completed: "
        f"{report['baseline_completed']}/"
        f"{report['expected_case_count']}"
    )

    print(
        f"Mitigated completed: "
        f"{report['mitigated_completed']}/"
        f"{report['expected_case_count']}"
    )

    print(
        f"Complete baseline: "
        f"{'YES' if report['complete_baseline'] else 'NO'}"
    )

    print(
        f"Complete mitigated: "
        f"{'YES' if report['complete_mitigated'] else 'NO'}"
    )

    print(
        f"Matching case sets: "
        f"{'YES' if report['matching_case_sets'] else 'NO'}"
    )

    print(
        f"Comparable cases: "
        f"{report['comparable_cases']}"
    )

    print(
        f"Winner changes: "
        f"{report['winner_changes']}"
    )

    print(
        f"Winner change rate: "
        f"{report['winner_change_rate']:.2%}"
    )

    print()

    print("Baseline:")

    print(
        f"  Position flips: "
        f"{report['baseline']['position_flips']}"
    )

    print(
        f"  Position flip rate: "
        f"{report['baseline']['position_flip_rate']:.2%}"
    )

    print(
        f"  Expected-winner matches: "
        f"{report['baseline']['expected_winner_matches']}"
    )

    print(
        f"  Expected-winner accuracy: "
        f"{report['baseline']['expected_winner_accuracy']:.2%}"
    )

    print()

    print("Mitigated:")

    print(
        f"  Position flips: "
        f"{report['mitigated']['position_flips']}"
    )

    print(
        f"  Position flip rate: "
        f"{report['mitigated']['position_flip_rate']:.2%}"
    )

    print(
        f"  Expected-winner matches: "
        f"{report['mitigated']['expected_winner_matches']}"
    )

    print(
        f"  Expected-winner accuracy: "
        f"{report['mitigated']['expected_winner_accuracy']:.2%}"
    )

    print()

    print(
        f"Report saved to: "
        f"{REPORT_FILE}"
    )


# ==========================================================
# MAIN
# ==========================================================

def main():
    report = build_report()

    save_report(
        report
    )

    print_report(
        report
    )


if __name__ == "__main__":
    main()