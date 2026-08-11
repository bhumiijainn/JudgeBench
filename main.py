import json
import sys
from pathlib import Path


# ==========================================================
# PATHS
# ==========================================================

DATASET_PATH = Path("data/test_suite.yaml")
ADVERSARIAL_PATH = Path("data/adversarial.yaml")
VERBOSITY_PATH = Path("data/verbosity_suite.yaml")
RESULT_DIR = Path("result")


# ==========================================================
# HELP
# ==========================================================

def show_help():
    print()
    print("JudgeBench")
    print("=" * 55)
    print()
    print("Commands:")
    print()
    print("  python main.py validate-dataset")
    print("  python main.py validate-adversarial")
    print("  python main.py validate-judge")
    print("  python main.py test-retest")
    print("  python main.py compare-ab")
    print("  python main.py validate-bias")
    print("  python main.py smoke-test")
    print("  python main.py judge-one <case_id>")
    print("  python main.py pairwise-one <case_id>")
    print("  python main.py run-adversarial")
    print("  python main.py run-verbosity baseline")
    print("  python main.py run-verbosity mitigated")
    print("  python main.py compare-verbosity")
    print("  python main.py report-verbosity")
    print("  python main.py scorecard")
    print()


# ==========================================================
# DATASET LOADING
# ==========================================================

def load_cases(path):
    from app.loader import load_test_suite

    return load_test_suite(str(path))


def find_case(case_id):
    cases = load_cases(DATASET_PATH)

    for case in cases:
        if case.get("id") == case_id:
            return case

    return None


# ==========================================================
# DATASET VALIDATION
# ==========================================================

def validate_dataset_command():
    try:
        cases = load_cases(DATASET_PATH)

        print()
        print(f"Loaded {len(cases)} cases.")

        if len(cases) != 30:
            print("Dataset validation: FAILED")
            print("Expected 30 cases.")
            return

        ids = [case.get("id") for case in cases]

        if len(ids) != len(set(ids)):
            print("Dataset validation: FAILED")
            print("Duplicate case IDs found.")
            return

        missing_candidates = []

        for case in cases:
            if (
                not case.get("candidate_a")
                or not case.get("candidate_b")
            ):
                missing_candidates.append(
                    case.get("id")
                )

        if missing_candidates:
            print("Dataset validation: FAILED")
            print("Cases missing candidates:")
            print(missing_candidates)
            return

        print("Dataset validation: PASSED")

    except Exception as exc:
        print("Dataset validation: FAILED")
        print(f"Reason: {exc}")


# ==========================================================
# ADVERSARIAL DATASET VALIDATION
# ==========================================================

def validate_adversarial_command():
    try:
        cases = load_cases(ADVERSARIAL_PATH)

        print()
        print(
            f"Loaded {len(cases)} "
            "adversarial cases."
        )

        if len(cases) != 10:
            print(
                "Adversarial dataset "
                "validation: FAILED"
            )
            print("Expected 10 cases.")
            return

        ids = [case.get("id") for case in cases]

        if len(ids) != len(set(ids)):
            print(
                "Adversarial dataset "
                "validation: FAILED"
            )
            print("Duplicate case IDs found.")
            return

        missing_winners = []

        for case in cases:
            if not case.get("expected_winner"):
                missing_winners.append(
                    case.get("id")
                )

        if missing_winners:
            print(
                "Adversarial dataset "
                "validation: FAILED"
            )
            print(
                "Cases missing expected "
                "winner:"
            )
            print(missing_winners)
            return

        print(
            "Adversarial dataset "
            "validation: PASSED"
        )

    except Exception as exc:
        print(
            "Adversarial dataset "
            "validation: FAILED"
        )
        print(f"Reason: {exc}")


# ==========================================================
# HUMAN / GOLD VALIDATION
# ==========================================================

def validate_judge():
    try:
        from app.judge_validation import (
            run_validation,
        )

        run_validation()

    except Exception as exc:
        print()
        print("Judge validation failed.")
        print(f"Reason: {exc}")


# ==========================================================
# TEST-RETEST VALIDATION
# ==========================================================

def test_retest():
    try:
        from app.test_retest import (
            run_test_retest,
        )

        run_test_retest()

    except Exception as exc:
        print()
        print(
            "Test-retest validation failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# A/B COMPARISON
# ==========================================================

def compare_ab():
    try:
        from app.ab_comparison import (
            run_ab_comparison,
        )

        run_ab_comparison(
            expected_cases=30
        )

    except Exception as exc:
        print()
        print(
            "A/B comparison failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# BIAS VALIDATION
# ==========================================================

def validate_bias():
    try:
        from app.bias_validation import (
            run_bias_validation,
        )

        run_bias_validation()

    except Exception as exc:
        print()
        print(
            "Bias validation failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# SMOKE TEST
# ==========================================================

def smoke_test():
    print()
    print("JudgeBench LLM Smoke Test")
    print("=" * 55)

    try:
        from app.config import (
            JUDGE_MODEL,
            JUDGE_TEMPERATURE,
        )

        from app.llm_client import LLMClient

        print(
            f"Judge model: {JUDGE_MODEL}"
        )

        print(
            f"Judge temperature: "
            f"{JUDGE_TEMPERATURE}"
        )

        print()

        client = LLMClient(
            model=JUDGE_MODEL,
            temperature=JUDGE_TEMPERATURE,
        )

        response = client.generate(
            prompt=(
                "Reply with exactly this text: "
                "JudgeBench API connection successful."
            ),
            purpose="smoke_test",
        )

        print("Response:")
        print(response.text)

        print()
        print("Metrics:")

        print(
            f"Model: "
            f"{response.model}"
        )

        print(
            f"Input tokens: "
            f"{response.input_tokens}"
        )

        print(
            f"Output tokens: "
            f"{response.output_tokens}"
        )

        print(
            f"Total tokens: "
            f"{response.input_tokens + response.output_tokens}"
        )

        print(
            f"Latency: "
            f"{response.latency_ms:.2f} ms"
        )

    except Exception as exc:
        print()
        print("Smoke test failed.")
        print(f"Reason: {exc}")


# ==========================================================
# POINTWISE JUDGE
# ==========================================================

def judge_one(case_id):
    case = find_case(case_id)

    if case is None:
        print(
            f"Case not found: {case_id}"
        )
        return

    candidate = case.get(
        "candidate_a"
    )

    if isinstance(candidate, dict):
        candidate_output = candidate.get(
            "output",
            "",
        )
    else:
        candidate_output = str(
            candidate or ""
        )

    if not candidate_output:
        print(
            f"No candidate output "
            f"found for {case_id}"
        )
        return

    try:
        from app.judge import Judge

        judge = Judge()

        print()
        print(
            f"Case: {case.get('id')}"
        )

        print(
            f"Category: "
            f"{case.get('category')}"
        )

        print(
            f"Difficulty: "
            f"{case.get('difficulty')}"
        )

        print()

        print(
            f"Input: "
            f"{case.get('input')}"
        )

        print(
            f"Model output: "
            f"{candidate_output}"
        )

        print()
        print("Calling judge...")

        verdict = judge.evaluate(case)

        print()
        print("## Verdict:")

        if hasattr(
            verdict,
            "criteria",
        ):
            for criterion in verdict.criteria:
                print(
                    f"{criterion.name}: "
                    f"{criterion.score}/5"
                )

                print(
                    criterion.rationale
                )

        print()

        print(
            f"Overall: "
            f"{verdict.overall_score}/5"
        )

        print(
            f"Passed: "
            f"{'YES' if verdict.passed else 'NO'}"
        )

        print()
        print("Summary:")
        print(verdict.summary)

    except Exception as exc:
        print()
        print("Judge failed.")
        print(f"Reason: {exc}")


# ==========================================================
# PAIRWISE JUDGE
# ==========================================================

def pairwise_one(case_id):
    case = find_case(case_id)

    if case is None:
        print(
            f"Case not found: {case_id}"
        )
        return

    candidate_a = case.get(
        "candidate_a"
    )

    candidate_b = case.get(
        "candidate_b"
    )

    if isinstance(
        candidate_a,
        dict,
    ):
        candidate_a = candidate_a.get(
            "output",
            "",
        )

    if isinstance(
        candidate_b,
        dict,
    ):
        candidate_b = candidate_b.get(
            "output",
            "",
        )

    if not candidate_a or not candidate_b:
        print(
            f"No candidates found "
            f"for {case_id}"
        )
        return

    try:
        from app.pairwise import PairwiseJudge

        print()
        print(
            f"Case: {case.get('id')}"
        )

        print(
            f"Category: "
            f"{case.get('category')}"
        )

        print(
            f"Difficulty: "
            f"{case.get('difficulty')}"
        )

        print()
        print("Candidate A:")
        print(candidate_a)

        print()
        print("Candidate B:")
        print(candidate_b)

        print()
        print(
            "Running A-first and "
            "B-first evaluations..."
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
            candidate_a=str(
                candidate_a
            ),
            candidate_b=str(
                candidate_b
            ),
        )

        print()
        print("## Pairwise Result:")

        print(
            f"A-first winner: "
            f"{result.first_order_winner}"
        )

        print(
            f"B-first winner: "
            f"{result.second_order_winner}"
        )

        print(
            f"Position flip: "
            f"{'YES' if result.position_flip else 'NO'}"
        )

        print(
            f"Final winner: "
            f"{result.final_winner}"
        )

        print()
        print("A-first reason:")
        print(
            result.first_order_reason
        )

        print()
        print("B-first reason:")
        print(
            result.second_order_reason
        )

        total_input = (
            result.first_order_input_tokens
            + result.second_order_input_tokens
        )

        total_output = (
            result.first_order_output_tokens
            + result.second_order_output_tokens
        )

        total_latency = (
            result.first_order_latency_ms
            + result.second_order_latency_ms
        )

        print()
        print("Pairwise metrics:")

        print(
            f"Input tokens: "
            f"{total_input}"
        )

        print(
            f"Output tokens: "
            f"{total_output}"
        )

        print(
            f"Total latency: "
            f"{total_latency:.2f} ms"
        )

        RESULT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            RESULT_DIR
            / f"{case_id}_pairwise.json"
        )

        if hasattr(
            result,
            "model_dump",
        ):
            data = result.model_dump()
        else:
            data = result.dict()

        output_path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

        print()
        print("Result saved:")
        print(output_path)

    except Exception as exc:
        print()
        print(
            "Pairwise evaluation failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# ADVERSARIAL RUNNER
# ==========================================================

def run_adversarial():
    try:
        from app.adversarial_runner import (
            run_adversarial_suite,
        )

        run_adversarial_suite()

    except Exception as exc:
        print()
        print(
            "Adversarial experiment "
            "failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# VERBOSITY RUNNER
# ==========================================================

def run_verbosity(mode):
    if mode not in {
        "baseline",
        "mitigated",
    }:
        print(
            "Invalid verbosity mode."
        )

        print()
        print("Use:")

        print(
            "  python main.py "
            "run-verbosity baseline"
        )

        print(
            "  python main.py "
            "run-verbosity mitigated"
        )

        return

    try:
        from app.verbosity_runner import (
            run_verbosity_experiment,
        )

        cases = load_cases(
            VERBOSITY_PATH
        )

        if not cases:
            print(
                "Verbosity dataset "
                "is empty."
            )
            return

        print()
        print(
            f"Loaded {len(cases)} "
            "verbosity cases."
        )

        run_verbosity_experiment(
            cases=cases,
            mode=mode,
        )

    except Exception as exc:
        print()
        print(
            "Verbosity experiment "
            "failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# VERBOSITY COMPARISON
# ==========================================================

def compare_verbosity():
    try:
        from app.verbosity_runner import (
            compare_verbosity_results,
        )

        cases = load_cases(
            VERBOSITY_PATH
        )

        if not cases:
            print(
                "Verbosity dataset "
                "is empty."
            )
            return

        compare_verbosity_results(
            cases
        )

    except Exception as exc:
        print()
        print(
            "Verbosity comparison "
            "failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# VERBOSITY REPORT
# ==========================================================

def report_verbosity():
    try:
        from app.verbosity_report import (
            main as report_main,
        )

        report_main()

    except Exception as exc:
        print()
        print(
            "Verbosity report failed."
        )
        print(f"Reason: {exc}")


# ==========================================================
# FINAL SCORECARD
# ==========================================================

def scorecard():
    try:
        from app.final_scorecard import (
            main as scorecard_main,
        )

        scorecard_main()

    except Exception as exc:
        print()
        print("Scorecard failed.")
        print(f"Reason: {exc}")


# ==========================================================
# MAIN
# ==========================================================

def main():
    args = sys.argv[1:]

    if not args:
        show_help()
        return

    command = args[0]

    # ------------------------------------------------------
    # DATASET VALIDATION
    # ------------------------------------------------------

    if command == "validate-dataset":
        validate_dataset_command()

    # ------------------------------------------------------
    # ADVERSARIAL DATASET VALIDATION
    # ------------------------------------------------------

    elif command == "validate-adversarial":
        validate_adversarial_command()

    # ------------------------------------------------------
    # HUMAN / GOLD VALIDATION
    # ------------------------------------------------------

    elif command == "validate-judge":
        validate_judge()

    # ------------------------------------------------------
    # TEST-RETEST
    # ------------------------------------------------------

    elif command == "test-retest":
        test_retest()

    # ------------------------------------------------------
    # A/B COMPARISON
    # ------------------------------------------------------

    elif command == "compare-ab":
        compare_ab()

    # ------------------------------------------------------
    # BIAS VALIDATION
    # ------------------------------------------------------

    elif command == "validate-bias":
        validate_bias()

    # ------------------------------------------------------
    # SMOKE TEST
    # ------------------------------------------------------

    elif command == "smoke-test":
        smoke_test()

    # ------------------------------------------------------
    # POINTWISE JUDGE
    # ------------------------------------------------------

    elif command == "judge-one":
        if len(args) < 2:
            print("Usage:")
            print(
                "python main.py "
                "judge-one <case_id>"
            )
            return

        judge_one(args[1])

    # ------------------------------------------------------
    # PAIRWISE JUDGE
    # ------------------------------------------------------

    elif command == "pairwise-one":
        if len(args) < 2:
            print("Usage:")
            print(
                "python main.py "
                "pairwise-one <case_id>"
            )
            return

        pairwise_one(args[1])

    # ------------------------------------------------------
    # ADVERSARIAL
    # ------------------------------------------------------

    elif command == "run-adversarial":
        run_adversarial()

    # ------------------------------------------------------
    # VERBOSITY
    # ------------------------------------------------------

    elif command == "run-verbosity":
        if len(args) < 2:
            print("Usage:")
            print(
                "python main.py "
                "run-verbosity baseline"
            )
            print(
                "python main.py "
                "run-verbosity mitigated"
            )
            return

        run_verbosity(args[1])

    # ------------------------------------------------------
    # VERBOSITY COMPARISON
    # ------------------------------------------------------

    elif command == "compare-verbosity":
        compare_verbosity()

    # ------------------------------------------------------
    # VERBOSITY REPORT
    # ------------------------------------------------------

    elif command == "report-verbosity":
        report_verbosity()

    # ------------------------------------------------------
    # FINAL SCORECARD
    # ------------------------------------------------------

    elif command == "scorecard":
        scorecard()

    # ------------------------------------------------------
    # UNKNOWN COMMAND
    # ------------------------------------------------------

    else:
        print(
            f"Unknown command: {command}"
        )

        show_help()


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()