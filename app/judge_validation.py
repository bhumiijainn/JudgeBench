import json
from pathlib import Path
from typing import Any


HUMAN_LABELS_PATH = Path(
    "data/human_labels.yaml"
)

RESULT_DIR = Path("result")

VALIDATION_RESULT_PATH = (
    RESULT_DIR / "judge_validation.json"
)


def load_human_labels(
    path: Path = HUMAN_LABELS_PATH,
) -> dict[str, str]:
    """
    Load human/gold winner labels from YAML.

    Expected structure:

    cases:
      - id: qa_001
        expected_winner: A
    """

    if not path.exists():
        raise FileNotFoundError(
            f"Human labels not found: {path}"
        )

    import yaml

    data = yaml.safe_load(
        path.read_text(
            encoding="utf-8"
        )
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Human labels root must be a YAML object."
        )

    cases = data.get("cases")

    if not isinstance(cases, list):
        raise ValueError(
            "Human labels must contain a 'cases' list."
        )

    labels: dict[str, str] = {}

    for case in cases:
        if not isinstance(case, dict):
            continue

        case_id = case.get("id")
        expected_winner = case.get(
            "expected_winner"
        )

        if not case_id:
            continue

        if expected_winner not in {
            "A",
            "B",
            "tie",
        }:
            raise ValueError(
                f"Invalid expected winner "
                f"for {case_id}: "
                f"{expected_winner}"
            )

        labels[str(case_id)] = (
            expected_winner
        )

    return labels


def load_pairwise_results(
    result_dir: Path = RESULT_DIR,
) -> dict[str, dict[str, Any]]:
    """
    Load completed pairwise result files.

    Only files matching *_pairwise.json
    are considered.
    """

    if not result_dir.exists():
        return {}

    results: dict[
        str,
        dict[str, Any],
    ] = {}

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

        case_id = data.get("case_id")
        final_winner = data.get(
            "final_winner"
        )

        if not case_id:
            continue

        if final_winner not in {
            "A",
            "B",
            "tie",
        }:
            continue

        results[str(case_id)] = data

    return results


def calculate_agreement(
    human_labels: dict[str, str],
    judge_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Compare human/gold labels with judge
    pairwise final winners.
    """

    comparable_ids = sorted(
        set(human_labels)
        & set(judge_results)
    )

    agreed_cases = []
    disagreed_cases = []

    for case_id in comparable_ids:
        human_winner = human_labels[
            case_id
        ]

        judge_winner = judge_results[
            case_id
        ]["final_winner"]

        if human_winner == judge_winner:
            agreed_cases.append(
                case_id
            )
        else:
            disagreed_cases.append(
                case_id
            )

    comparable_count = len(
        comparable_ids
    )

    agreed_count = len(
        agreed_cases
    )

    disagreed_count = len(
        disagreed_cases
    )

    if comparable_count:
        agreement_rate = (
            agreed_count
            / comparable_count
        )
    else:
        agreement_rate = 0.0

    # Cohen's kappa is not meaningful when
    # the human labels contain only one class.
    human_classes = set(
        human_labels.values()
    )

    if len(human_classes) < 2:
        cohen_kappa = None
        kappa_reason = (
            "Cohen's kappa is unavailable "
            "because the human/gold labels "
            "contain only one class."
        )
    elif comparable_count == 0:
        cohen_kappa = None
        kappa_reason = (
            "Cohen's kappa is unavailable "
            "because there are no comparable "
            "cases."
        )
    else:
        cohen_kappa, kappa_reason = (
            calculate_cohen_kappa(
                human_labels,
                judge_results,
                comparable_ids,
            )
        )

    return {
        "human_label_cases": len(
            human_labels
        ),
        "judge_result_cases": len(
            judge_results
        ),
        "comparable_cases":
            comparable_count,
        "agreed_cases":
            agreed_count,
        "disagreed_cases":
            disagreed_count,
        "agreement_rate":
            round(
                agreement_rate,
                4,
            ),
        "agreement_percent":
            round(
                agreement_rate * 100,
                2,
            ),
        "cohen_kappa":
            cohen_kappa,
        "cohen_kappa_reason":
            kappa_reason,
        "agreed_case_ids":
            agreed_cases,
        "disagreed_case_ids":
            disagreed_cases,
        "complete":
            comparable_count
            == len(human_labels),
    }


def calculate_cohen_kappa(
    human_labels: dict[str, str],
    judge_results: dict[str, dict[str, Any]],
    comparable_ids: list[str],
):
    """
    Calculate Cohen's kappa manually.

    This function is only reached when the
    human labels contain at least two classes.
    """

    if not comparable_ids:
        return (
            None,
            "No comparable cases.",
        )

    human_values = [
        human_labels[case_id]
        for case_id in comparable_ids
    ]

    judge_values = [
        judge_results[case_id][
            "final_winner"
        ]
        for case_id in comparable_ids
    ]

    observed = sum(
        human == judge
        for human, judge in zip(
            human_values,
            judge_values,
        )
    ) / len(comparable_ids)

    classes = sorted(
        set(human_values)
        | set(judge_values)
    )

    human_counts = {
        label: human_values.count(label)
        for label in classes
    }

    judge_counts = {
        label: judge_values.count(label)
        for label in classes
    }

    total = len(comparable_ids)

    expected = sum(
        (
            human_counts[label]
            / total
        )
        * (
            judge_counts[label]
            / total
        )
        for label in classes
    )

    if expected == 1.0:
        return (
            None,
            "Cohen's kappa is undefined "
            "because expected agreement is 1."
        )

    kappa = (
        (observed - expected)
        / (1.0 - expected)
    )

    return (
        round(kappa, 4),
        "Calculated successfully.",
    )


def build_validation_report(
    human_labels: dict[str, str],
    judge_results: dict[str, dict[str, Any]],
) -> dict[str, Any]:

    agreement = calculate_agreement(
        human_labels,
        judge_results,
    )

    return {
        "benchmark": "JudgeBench",
        "validation_type":
            "human_gold_agreement",
        "source": {
            "human_labels":
                str(HUMAN_LABELS_PATH),
            "judge_results":
                str(RESULT_DIR),
        },
        "metrics": agreement,
        "status": (
            "COMPLETE"
            if agreement["complete"]
            else "INCOMPLETE"
        ),
    }


def save_validation_report(
    report: dict[str, Any],
    path: Path = VALIDATION_RESULT_PATH,
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


def run_validation():
    human_labels = load_human_labels()

    judge_results = (
        load_pairwise_results()
    )

    report = build_validation_report(
        human_labels,
        judge_results,
    )

    save_validation_report(
        report
    )

    metrics = report["metrics"]

    print()
    print(
        "=================================================="
    )
    print(
        "JUDGEBENCH HUMAN/GOLD VALIDATION"
    )
    print(
        "=================================================="
    )

    print(
        f"Human-labeled cases: "
        f"{metrics['human_label_cases']}"
    )

    print(
        f"Judge pairwise results: "
        f"{metrics['judge_result_cases']}"
    )

    print(
        f"Comparable cases: "
        f"{metrics['comparable_cases']}"
    )

    print(
        f"Agreed cases: "
        f"{metrics['agreed_cases']}"
    )

    print(
        f"Disagreed cases: "
        f"{metrics['disagreed_cases']}"
    )

    print(
        f"Agreement rate: "
        f"{metrics['agreement_percent']:.2f}%"
    )

    if metrics["cohen_kappa"] is None:
        print(
            "Cohen's kappa: N/A"
        )

        print(
            f"Reason: "
            f"{metrics['cohen_kappa_reason']}"
        )
    else:
        print(
            f"Cohen's kappa: "
            f"{metrics['cohen_kappa']:.4f}"
        )

    print()

    print(
        f"Status: "
        f"{report['status']}"
    )

    print()

    print(
        "Validation report saved to: "
        f"{VALIDATION_RESULT_PATH}"
    )

    return report


def main():
    run_validation()


if __name__ == "__main__":
    main()