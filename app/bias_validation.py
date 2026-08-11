import json
from pathlib import Path
from typing import Any


RESULT_DIR = Path("result")

BIAS_VALIDATION_PATH = (
    RESULT_DIR / "bias_validation_summary.json"
)


def load_json(path: Path) -> dict[str, Any]:
    """
    Safely load a JSON result file.

    Missing or malformed result files return an
    empty dictionary so the summary can report
    incomplete evidence instead of crashing.
    """

    if not path.exists():
        return {}

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, dict):
            return data

    except (
        json.JSONDecodeError,
        OSError,
    ):
        pass

    return {}


# ==========================================================
# POSITION BIAS
# ==========================================================

def build_position_bias_section():
    data = load_json(
        RESULT_DIR
        / "adversarial_position_bias.json"
    )

    if not data:
        return {
            "bias": "position",
            "description": (
                "The judge may prefer whichever "
                "candidate appears first."
            ),
            "mitigation": (
                "Evaluate every pair in both "
                "A-first and B-first orders."
            ),
            "measurement": {},
            "status": "NO_DATA",
        }

    return {
        "bias": "position",
        "description": (
            "The judge may prefer whichever "
            "candidate appears first."
        ),
        "mitigation": (
            "Evaluate every pair in both "
            "A-first and B-first orders."
        ),
        "measurement": data,
        "status": "MEASURED",
    }


# ==========================================================
# VERBOSITY BIAS
# ==========================================================

def build_verbosity_bias_section():
    data = load_json(
        RESULT_DIR
        / "verbosity_comparison.json"
    )

    report = load_json(
        RESULT_DIR
        / "verbosity_report.json"
    )

    measurement = {}

    if data:
        measurement[
            "comparison"
        ] = data

    if report:
        measurement[
            "report"
        ] = report

    if not measurement:
        return {
            "bias": "verbosity",
            "description": (
                "The judge may prefer longer or "
                "more detailed answers even when "
                "the additional content is not "
                "useful or supported."
            ),
            "mitigation": (
                "Use explicit length-sensitive "
                "evaluation and compare baseline "
                "answers against verbosity-mitigated "
                "evaluation."
            ),
            "measurement": {},
            "status": "NO_DATA",
        }

    return {
        "bias": "verbosity",
        "description": (
            "The judge may prefer longer or "
            "more detailed answers even when "
            "the additional content is not "
            "useful or supported."
        ),
        "mitigation": (
            "Use explicit length-sensitive "
            "evaluation and compare baseline "
            "answers against verbosity-mitigated "
            "evaluation."
        ),
        "measurement": measurement,
        "status": "MEASURED",
    }


# ==========================================================
# SELF-ENHANCEMENT
# ==========================================================

def build_self_enhancement_section():
    return {
        "bias": "self_enhancement",
        "description": (
            "A judge may favor outputs generated "
            "by its own model family."
        ),
        "mitigation": (
            "Judge and generator are configurable "
            "independently so the judge can be "
            "selected from a different model family "
            "than the generator."
        ),
        "measurement": {
            "implemented": True,
            "empirical_measurement": False,
        },
        "status": "MITIGATION_IMPLEMENTED",
    }


# ==========================================================
# SYCOPHANCY / STYLE
# ==========================================================

def build_sycophancy_section():
    adversarial = load_json(
        RESULT_DIR
        / "adversarial_cases.json"
    )

    categories = []

    if isinstance(
        adversarial,
        list,
    ):
        categories = [
            item.get("category")
            for item in adversarial
            if isinstance(item, dict)
        ]

    elif isinstance(
        adversarial,
        dict,
    ):
        cases = adversarial.get(
            "cases",
            [],
        )

        if isinstance(
            cases,
            list,
        ):
            categories = [
                item.get("category")
                for item in cases
                if isinstance(item, dict)
            ]

    confidently_wrong = (
        "confidently_wrong"
        in categories
    )

    return {
        "bias": "sycophancy",
        "description": (
            "The judge may be influenced by "
            "confident presentation or persuasive "
            "style instead of correctness."
        ),
        "mitigation": (
            "Require per-criterion grounding "
            "and include confidently-wrong "
            "adversarial probes."
        ),
        "measurement": {
            "confidently_wrong_probe_present":
                confidently_wrong,
            "adversarial_result_available":
                bool(adversarial),
        },
        "status": (
            "MEASURED"
            if adversarial
            else "NO_DATA"
        ),
    }


# ==========================================================
# SCORE CLUSTERING
# ==========================================================

def build_score_clustering_section():
    return {
        "bias": "score_clustering",
        "description": (
            "Pointwise judges may cluster scores "
            "around a narrow portion of the scale "
            "and make absolute scores less "
            "discriminative."
        ),
        "mitigation": (
            "Use pairwise A-vs-B evaluation for "
            "comparative decisions instead of "
            "depending exclusively on an absolute "
            "pointwise score."
        ),
        "measurement": {
            "pairwise_evaluation_available":
                True,
            "few_shot_calibration":
                False,
        },
        "status": "MITIGATED_BY_PAIRWISE",
    }


# ==========================================================
# HUMAN / GOLD VALIDATION
# ==========================================================

def build_human_validation_section():
    data = load_json(
        RESULT_DIR
        / "judge_validation.json"
    )

    if not data:
        return {
            "validation": "human_gold_agreement",
            "measurement": {},
            "status": "NO_DATA",
        }

    return {
        "validation": "human_gold_agreement",
        "measurement": data.get(
            "metrics",
            {},
        ),
        "status": data.get(
            "status",
            "UNKNOWN",
        ),
    }


# ==========================================================
# TEST-RETEST
# ==========================================================

def build_test_retest_section():
    data = load_json(
        RESULT_DIR
        / "test_retest.json"
    )

    if not data:
        return {
            "validation":
                "test_retest_consistency",
            "measurement": {},
            "status": "NO_DATA",
        }

    return {
        "validation":
            "test_retest_consistency",
        "measurement": data.get(
            "metrics",
            {},
        ),
        "status": data.get(
            "status",
            "UNKNOWN",
        ),
    }


# ==========================================================
# ADVERSARIAL VALIDATION
# ==========================================================

def build_adversarial_section():
    data = load_json(
        RESULT_DIR
        / "adversarial_cases.json"
    )

    if not data:
        return {
            "validation":
                "adversarial_probe_set",
            "measurement": {},
            "status": "NO_DATA",
        }

    if isinstance(
        data,
        list,
    ):
        cases = data
    else:
        cases = data.get(
            "cases",
            [],
        )

    total = len(cases)

    correct = sum(
        1
        for case in cases
        if case.get(
            "expected_winner_match",
            False,
        )
    )

    flips = sum(
        1
        for case in cases
        if case.get(
            "position_flip",
            False,
        )
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    flip_rate = (
        flips / total
        if total
        else 0.0
    )

    return {
        "validation":
            "adversarial_probe_set",
        "measurement": {
            "cases": total,
            "correct_expected_winner":
                correct,
            "expected_winner_accuracy":
                round(
                    accuracy,
                    4,
                ),
            "position_flips":
                flips,
            "position_flip_rate":
                round(
                    flip_rate,
                    4,
                ),
        },
        "status": (
            "MEASURED"
            if total
            else "NO_DATA"
        ),
    }


# ==========================================================
# OVERALL STATUS
# ==========================================================

def calculate_overall_status(
    sections,
):
    """
    Determine whether the evidence package is
    complete.

    A mitigation can be implemented without
    having empirical measurements yet.
    """

    empirical_sections = [
        sections["position_bias"],
        sections["verbosity_bias"],
        sections["sycophancy"],
        sections["human_validation"],
        sections["test_retest"],
        sections["adversarial_validation"],
    ]

    measured_count = sum(
        1
        for section in empirical_sections
        if section.get("status")
        in {
            "MEASURED",
            "COMPLETE",
        }
    )

    total_count = len(
        empirical_sections
    )

    if measured_count == total_count:
        return "COMPLETE"

    if measured_count > 0:
        return "PARTIAL"

    return "INCOMPLETE"


# ==========================================================
# BUILD SUMMARY
# ==========================================================

def build_summary():
    sections = {
        "position_bias":
            build_position_bias_section(),

        "verbosity_bias":
            build_verbosity_bias_section(),

        "self_enhancement":
            build_self_enhancement_section(),

        "sycophancy":
            build_sycophancy_section(),

        "score_clustering":
            build_score_clustering_section(),

        "human_validation":
            build_human_validation_section(),

        "test_retest":
            build_test_retest_section(),

        "adversarial_validation":
            build_adversarial_section(),
    }

    return {
        "benchmark": "JudgeBench",
        "artifact":
            "bias_validation_summary",
        "biases_evaluated": [
            "position",
            "verbosity",
            "self_enhancement",
            "sycophancy",
            "score_clustering",
        ],
        "sections": sections,
        "overall_status":
            calculate_overall_status(
                sections
            ),
    }


# ==========================================================
# SAVE
# ==========================================================

def save_summary(
    summary,
    path=BIAS_VALIDATION_PATH,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )


# ==========================================================
# CLI
# ==========================================================

def run_bias_validation():
    summary = build_summary()

    save_summary(summary)

    print()
    print(
        "=================================================="
    )
    print(
        "JUDGEBENCH BIAS VALIDATION SUMMARY"
    )
    print(
        "=================================================="
    )

    sections = summary[
        "sections"
    ]

    print()

    print(
        "POSITION BIAS"
    )

    print(
        f"  Status: "
        f"{sections['position_bias']['status']}"
    )

    print()

    print(
        "VERBOSITY BIAS"
    )

    print(
        f"  Status: "
        f"{sections['verbosity_bias']['status']}"
    )

    print()

    print(
        "SELF-ENHANCEMENT"
    )

    print(
        f"  Status: "
        f"{sections['self_enhancement']['status']}"
    )

    print()

    print(
        "SYCOPHANCY"
    )

    print(
        f"  Status: "
        f"{sections['sycophancy']['status']}"
    )

    print()

    print(
        "SCORE CLUSTERING"
    )

    print(
        f"  Status: "
        f"{sections['score_clustering']['status']}"
    )

    print()

    print(
        "HUMAN / GOLD VALIDATION"
    )

    print(
        f"  Status: "
        f"{sections['human_validation']['status']}"
    )

    human_metrics = sections[
        "human_validation"
    ].get(
        "measurement",
        {},
    )

    if human_metrics:
        if (
            "agreement_percent"
            in human_metrics
        ):
            print(
                f"  Agreement: "
                f"{human_metrics['agreement_percent']:.2f}%"
            )

    print()

    print(
        "TEST-RETEST"
    )

    print(
        f"  Status: "
        f"{sections['test_retest']['status']}"
    )

    retest_metrics = sections[
        "test_retest"
    ].get(
        "measurement",
        {},
    )

    if retest_metrics:
        if (
            "consistency_percent"
            in retest_metrics
        ):
            print(
                f"  Consistency: "
                f"{retest_metrics['consistency_percent']:.2f}%"
            )

        if (
            "flip_percent"
            in retest_metrics
        ):
            print(
                f"  Flip rate: "
                f"{retest_metrics['flip_percent']:.2f}%"
            )

    print()

    print(
        "ADVERSARIAL VALIDATION"
    )

    print(
        f"  Status: "
        f"{sections['adversarial_validation']['status']}"
    )

    adversarial_metrics = sections[
        "adversarial_validation"
    ].get(
        "measurement",
        {},
    )

    if adversarial_metrics:
        print(
            f"  Cases: "
            f"{adversarial_metrics.get('cases', 0)}"
        )

        print(
            f"  Expected-winner accuracy: "
            f"{adversarial_metrics.get('expected_winner_accuracy', 0):.2%}"
        )

        print(
            f"  Position-flip rate: "
            f"{adversarial_metrics.get('position_flip_rate', 0):.2%}"
        )

    print()

    print(
        "=================================================="
    )

    print(
        f"Overall status: "
        f"{summary['overall_status']}"
    )

    print()

    print(
        "Bias validation summary saved to: "
        f"{BIAS_VALIDATION_PATH}"
    )

    return summary


def main():
    run_bias_validation()


if __name__ == "__main__":
    main()