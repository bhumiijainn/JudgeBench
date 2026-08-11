import json
from pathlib import Path


RESULT_DIR = Path("result")

ADVERSARIAL_REPORT = (
    RESULT_DIR
    / "adversarial_position_bias.json"
)

VERBOSITY_REPORT = (
    RESULT_DIR
    / "verbosity_report.json"
)

SCORECARD_FILE = (
    RESULT_DIR
    / "final_scorecard.json"
)

EXPECTED_CASE_COUNT = 10


# ==========================================================
# LOAD JSON
# ==========================================================

def load_json(path):
    if not path.exists():
        return None

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


# ==========================================================
# BUILD SCORECARD
# ==========================================================

def build_scorecard():
    adversarial = load_json(
        ADVERSARIAL_REPORT
    )

    verbosity = load_json(
        VERBOSITY_REPORT
    )

    scorecard = {
        "benchmark": "JudgeBench",
        "status": "INCOMPLETE",
        "adversarial": None,
        "verbosity": None,
        "summary": {},
    }

    # ======================================================
    # ADVERSARIAL
    # ======================================================

    if adversarial is not None:
        completed = adversarial.get(
            "completed_cases",
            0,
        )

        position_flips = adversarial.get(
            "position_flips",
            0,
        )

        position_flip_rate = adversarial.get(
            "position_flip_rate",
            0.0,
        )

        expected_accuracy = adversarial.get(
            "expected_winner_accuracy",
            0.0,
        )

        scorecard["adversarial"] = {
            "completed_cases": completed,
            "expected_cases": EXPECTED_CASE_COUNT,
            "position_flips": position_flips,
            "position_flip_rate":
                position_flip_rate,
            "expected_winner_accuracy":
                expected_accuracy,
            "complete":
                completed == EXPECTED_CASE_COUNT,
        }

    # ======================================================
    # VERBOSITY
    # ======================================================

    if verbosity is not None:
        baseline_completed = verbosity.get(
            "baseline_completed",
            0,
        )

        mitigated_completed = verbosity.get(
            "mitigated_completed",
            0,
        )

        comparable_cases = verbosity.get(
            "comparable_cases",
            0,
        )

        matching_case_sets = verbosity.get(
            "matching_case_sets",
            False,
        )

        baseline = verbosity.get(
            "baseline",
            {},
        )

        mitigated = verbosity.get(
            "mitigated",
            {},
        )

        baseline_flip_rate = baseline.get(
            "position_flip_rate",
            0.0,
        )

        mitigated_flip_rate = mitigated.get(
            "position_flip_rate",
            0.0,
        )

        baseline_accuracy = baseline.get(
            "expected_winner_accuracy",
            0.0,
        )

        mitigated_accuracy = mitigated.get(
            "expected_winner_accuracy",
            0.0,
        )

        complete = (
            baseline_completed
            == EXPECTED_CASE_COUNT
            and mitigated_completed
            == EXPECTED_CASE_COUNT
            and comparable_cases
            == EXPECTED_CASE_COUNT
            and matching_case_sets
        )

        scorecard["verbosity"] = {
            "baseline_completed":
                baseline_completed,

            "mitigated_completed":
                mitigated_completed,

            "comparable_cases":
                comparable_cases,

            "matching_case_sets":
                matching_case_sets,

            "baseline_position_flip_rate":
                baseline_flip_rate,

            "mitigated_position_flip_rate":
                mitigated_flip_rate,

            "position_bias_change":
                round(
                    baseline_flip_rate
                    - mitigated_flip_rate,
                    4,
                ),

            "baseline_expected_winner_accuracy":
                baseline_accuracy,

            "mitigated_expected_winner_accuracy":
                mitigated_accuracy,

            "accuracy_change":
                round(
                    mitigated_accuracy
                    - baseline_accuracy,
                    4,
                ),

            "complete":
                complete,
        }

    # ======================================================
    # OVERALL COMPLETION
    # ======================================================

    adversarial_complete = (
        scorecard["adversarial"]
        is not None
        and scorecard["adversarial"]["complete"]
    )

    verbosity_complete = (
        scorecard["verbosity"]
        is not None
        and scorecard["verbosity"]["complete"]
    )

    if (
        adversarial_complete
        and verbosity_complete
    ):
        scorecard["status"] = "COMPLETE"

    # ======================================================
    # INTERPRETATION
    # ======================================================

    if (
        scorecard["verbosity"] is None
        or not scorecard["verbosity"]["complete"]
    ):
        interpretation = (
            "Experiment incomplete — "
            "insufficient comparable "
            "verbosity cases for interpretation."
        )

    else:
        bias_change = scorecard[
            "verbosity"
        ]["position_bias_change"]

        accuracy_change = scorecard[
            "verbosity"
        ]["accuracy_change"]

        if (
            bias_change > 0
            and accuracy_change >= 0
        ):
            interpretation = (
                "Mitigation reduced "
                "position bias without "
                "reducing expected-winner "
                "accuracy."
            )

        elif (
            bias_change > 0
            and accuracy_change < 0
        ):
            interpretation = (
                "Mitigation reduced "
                "position bias but also "
                "reduced expected-winner "
                "accuracy."
            )

        elif bias_change == 0:
            interpretation = (
                "No measurable change "
                "in position bias."
            )

        else:
            interpretation = (
                "Mitigation increased "
                "position bias."
            )

    scorecard["summary"] = {
        "interpretation":
            interpretation,
    }

    return scorecard


# ==========================================================
# SAVE SCORECARD
# ==========================================================

def save_scorecard(scorecard):
    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    SCORECARD_FILE.write_text(
        json.dumps(
            scorecard,
            indent=2,
        ),
        encoding="utf-8",
    )


# ==========================================================
# PRINT SCORECARD
# ==========================================================

def print_scorecard(scorecard):
    print()
    print(
        "=================================================="
    )
    print(
        "JUDGEBENCH FINAL SCORECARD"
    )
    print(
        "=================================================="
    )

    print(
        f"Status: "
        f"{scorecard['status']}"
    )

    print()

    # ------------------------------------------------------
    # ADVERSARIAL
    # ------------------------------------------------------

    if scorecard["adversarial"]:
        adversarial = scorecard[
            "adversarial"
        ]

        print("ADVERSARIAL")

        print(
            f"  Cases: "
            f"{adversarial['completed_cases']}/"
            f"{adversarial['expected_cases']}"
        )

        print(
            f"  Position flips: "
            f"{adversarial['position_flips']}"
        )

        print(
            f"  Position-flip rate: "
            f"{adversarial['position_flip_rate']:.2%}"
        )

        print(
            f"  Expected-winner accuracy: "
            f"{adversarial['expected_winner_accuracy']:.2%}"
        )

        print(
            f"  Complete: "
            f"{'YES' if adversarial['complete'] else 'NO'}"
        )

    else:
        print(
            "ADVERSARIAL: NO REPORT"
        )

    print()

    # ------------------------------------------------------
    # VERBOSITY
    # ------------------------------------------------------

    if scorecard["verbosity"]:
        verbosity = scorecard[
            "verbosity"
        ]

        print("VERBOSITY")

        print(
            f"  Baseline: "
            f"{verbosity['baseline_completed']}/"
            f"{EXPECTED_CASE_COUNT}"
        )

        print(
            f"  Mitigated: "
            f"{verbosity['mitigated_completed']}/"
            f"{EXPECTED_CASE_COUNT}"
        )

        print(
            f"  Comparable cases: "
            f"{verbosity['comparable_cases']}"
        )

        print(
            f"  Matching case sets: "
            f"{'YES' if verbosity['matching_case_sets'] else 'NO'}"
        )

        print(
            f"  Complete: "
            f"{'YES' if verbosity['complete'] else 'NO'}"
        )

        print(
            f"  Baseline flip rate: "
            f"{verbosity['baseline_position_flip_rate']:.2%}"
        )

        print(
            f"  Mitigated flip rate: "
            f"{verbosity['mitigated_position_flip_rate']:.2%}"
        )

        print(
            f"  Bias change: "
            f"{verbosity['position_bias_change']:.2%}"
        )

        print(
            f"  Baseline accuracy: "
            f"{verbosity['baseline_expected_winner_accuracy']:.2%}"
        )

        print(
            f"  Mitigated accuracy: "
            f"{verbosity['mitigated_expected_winner_accuracy']:.2%}"
        )

        print(
            f"  Accuracy change: "
            f"{verbosity['accuracy_change']:.2%}"
        )

    else:
        print(
            "VERBOSITY: NO REPORT"
        )

    print()

    # ------------------------------------------------------
    # INTERPRETATION
    # ------------------------------------------------------

    print(
        "INTERPRETATION"
    )

    print(
        scorecard["summary"][
            "interpretation"
        ]
    )

    print()

    print(
        f"Scorecard saved to: "
        f"{SCORECARD_FILE}"
    )


# ==========================================================
# MAIN
# ==========================================================

def main():
    scorecard = build_scorecard()

    save_scorecard(
        scorecard
    )

    print_scorecard(
        scorecard
    )


if __name__ == "__main__":
    main()