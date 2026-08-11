import json
from pathlib import Path
from typing import Any

from app.pairwise import PairwiseJudge


RESULT_ROOT = Path("result")
BASELINE_DIR = RESULT_ROOT / "baseline"
MITIGATED_DIR = RESULT_ROOT / "mitigated"


def _ensure_directories() -> None:
    BASELINE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    MITIGATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def _result_path(
    mode: str,
) -> Path:
    if mode == "baseline":
        return (
            BASELINE_DIR
            / "verbosity_cases.json"
        )

    if mode == "mitigated":
        return (
            MITIGATED_DIR
            / "verbosity_cases.json"
        )

    raise ValueError(
        "mode must be 'baseline' or 'mitigated'"
    )


def _load_completed(
    mode: str,
) -> dict[str, dict[str, Any]]:
    path = _result_path(mode)

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

    if not isinstance(data, list):
        return {}

    completed = {}

    for item in data:
        if not isinstance(item, dict):
            continue

        case_id = item.get("case_id")

        if case_id:
            completed[
                case_id
            ] = item

    return completed


def _save_results(
    mode: str,
    results: dict[str, dict[str, Any]],
) -> None:
    path = _result_path(mode)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ordered_results = list(
        results.values()
    )

    path.write_text(
        json.dumps(
            ordered_results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _case_value(
    case: dict[str, Any],
    key: str,
    default: str = "",
) -> str:
    value = case.get(key)

    if value is None:
        return default

    if isinstance(value, dict):
        output = value.get("output")

        if output is not None:
            return str(output)

    return str(value)


def _evaluate_case(
    judge: PairwiseJudge,
    case: dict[str, Any],
) -> dict[str, Any]:
    case_id = str(
        case["id"]
    )

    user_input = _case_value(
        case,
        "input",
    )

    system_prompt = _case_value(
        case,
        "system_prompt",
    )

    candidate_a = _case_value(
        case,
        "candidate_a",
    )

    candidate_b = _case_value(
        case,
        "candidate_b",
    )

    result = judge.evaluate(
        case_id=case_id,
        user_input=user_input,
        system_prompt=system_prompt,
        candidate_a=candidate_a,
        candidate_b=candidate_b,
    )

    return result.model_dump()


def run_verbosity_experiment(
    cases: list[dict[str, Any]],
    mode: str,
    model: str | None = None,
    temperature: float = 0.0,
) -> None:
    """
    Run one controlled experiment condition.

    baseline:
        mitigation_enabled=False

    mitigated:
        mitigation_enabled=True
    """

    if mode not in {
        "baseline",
        "mitigated",
    }:
        raise ValueError(
            "mode must be 'baseline' or 'mitigated'"
        )

    _ensure_directories()

    mitigation_enabled = (
        mode == "mitigated"
    )

    judge = PairwiseJudge(
        model=model,
        temperature=temperature,
        mitigation_enabled=mitigation_enabled,
    )

    completed = _load_completed(
        mode
    )

    print()
    print(
        "=" * 55
    )
    print(
        f"VERBOSITY EXPERIMENT: {mode.upper()}"
    )
    print(
        "=" * 55
    )

    print(
        f"Mitigation enabled: "
        f"{mitigation_enabled}"
    )

    print(
        f"Cases: {len(cases)}"
    )

    if completed:
        print(
            f"Already completed: "
            f"{len(completed)}"
        )

    for index, case in enumerate(
        cases,
        start=1,
    ):
        case_id = str(
            case["id"]
        )

        print()
        print(
            f"[{index}/{len(cases)}] "
            f"{case_id}"
        )

        if case_id in completed:
            print(
                "Already completed — skipping."
            )
            continue

        try:
            result = _evaluate_case(
                judge,
                case,
            )

        except Exception as exc:
            print()
            print(
                "Evaluation stopped."
            )
            print(
                f"Reason: {exc}"
            )
            print(
                "Completed results have "
                "already been saved."
            )
            break

        completed[
            case_id
        ] = result

        _save_results(
            mode,
            completed,
        )

        print(
            f"  A-first: "
            f"{result['first_order_winner']}"
        )

        print(
            f"  B-first: "
            f"{result['second_order_winner']}"
        )

        print(
            f"  Final: "
            f"{result['final_winner']}"
        )

        print(
            "  Position flip: "
            f"{'YES' if result['position_flip'] else 'NO'}"
        )

        print(
            "  Saved immediately."
        )

    print()
    print(
        "=" * 55
    )

    print(
        f"{mode.upper()} COMPLETED: "
        f"{len(completed)}/{len(cases)}"
    )

    print(
        f"Results saved to: "
        f"{_result_path(mode)}"
    )


def _winner_change(
    baseline: dict[str, Any],
    mitigated: dict[str, Any],
) -> bool:
    return (
        baseline.get("final_winner")
        != mitigated.get("final_winner")
    )


def compare_verbosity_results(
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    baseline = _load_completed(
        "baseline"
    )

    mitigated = _load_completed(
        "mitigated"
    )

    comparable_ids = [
        str(case["id"])
        for case in cases
        if str(case["id"]) in baseline
        and str(case["id"]) in mitigated
    ]

    winner_changes = 0
    baseline_flips = 0
    mitigated_flips = 0

    comparisons = []

    for case_id in comparable_ids:
        base = baseline[
            case_id
        ]

        mitigated_result = mitigated[
            case_id
        ]

        baseline_flip = bool(
            base.get(
                "position_flip",
                False,
            )
        )

        mitigated_flip = bool(
            mitigated_result.get(
                "position_flip",
                False,
            )
        )

        if baseline_flip:
            baseline_flips += 1

        if mitigated_flip:
            mitigated_flips += 1

        changed = _winner_change(
            base,
            mitigated_result,
        )

        if changed:
            winner_changes += 1

        comparisons.append(
            {
                "case_id": case_id,
                "baseline_winner": base.get(
                    "final_winner"
                ),
                "mitigated_winner": mitigated_result.get(
                    "final_winner"
                ),
                "winner_changed": changed,
                "baseline_position_flip": baseline_flip,
                "mitigated_position_flip": mitigated_flip,
            }
        )

    total = len(
        comparable_ids
    )

    report = {
        "experiment": (
            "verbosity_mitigation"
        ),
        "comparable_cases": total,
        "winner_changes": winner_changes,
        "winner_change_rate": (
            winner_changes / total
            if total
            else 0.0
        ),
        "baseline_position_flips": (
            baseline_flips
        ),
        "baseline_position_flip_rate": (
            baseline_flips / total
            if total
            else 0.0
        ),
        "mitigated_position_flips": (
            mitigated_flips
        ),
        "mitigated_position_flip_rate": (
            mitigated_flips / total
            if total
            else 0.0
        ),
        "comparisons": comparisons,
    }

    _ensure_directories()

    output_path = (
        RESULT_ROOT
        / "verbosity_comparison.json"
    )

    output_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "=" * 55
    )
    print(
        "VERBOSITY MITIGATION COMPARISON"
    )
    print(
        "=" * 55
    )

    print(
        f"Comparable cases: {total}"
    )

    print(
        f"Winner changes: "
        f"{winner_changes}"
    )

    print(
        f"Winner change rate: "
        f"{report['winner_change_rate']:.2%}"
    )

    print(
        f"Baseline position flips: "
        f"{baseline_flips}"
    )

    print(
        f"Mitigated position flips: "
        f"{mitigated_flips}"
    )

    print()
    print(
        f"Comparison saved to: "
        f"{output_path}"
    )

    return report