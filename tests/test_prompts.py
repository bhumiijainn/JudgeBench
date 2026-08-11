from app.prompts import build_judge_prompt

from app.pairwise import build_pairwise_prompt

from app.verbosity_mitigation import (
    VERBOSITY_MITIGATION_INSTRUCTIONS,
)


def test_judge_prompt_contains_case_information():
    prompt = build_judge_prompt(
        case_id="qa_001",
        user_input="What is the capital of France?",
        system_prompt=(
            "Answer factual questions accurately "
            "and concisely."
        ),
        model_output="Paris.",
        criteria=[
            "correctness",
            "completeness",
            "instruction_following",
        ],
    )

    assert "qa_001" in prompt
    assert "What is the capital of France?" in prompt
    assert "Paris." in prompt


def test_judge_prompt_contains_rubric():
    prompt = build_judge_prompt(
        case_id="qa_001",
        user_input="What is 2 + 2?",
        system_prompt="Answer accurately.",
        model_output="4",
        criteria=[
            "correctness",
            "completeness",
            "instruction_following",
        ],
    )

    assert "correctness" in prompt
    assert "completeness" in prompt
    assert "instruction_following" in prompt


def test_reference_output_is_optional():
    prompt = build_judge_prompt(
        case_id="qa_001",
        user_input="What is 2 + 2?",
        system_prompt="Answer accurately.",
        model_output="4",
        criteria=[
            "correctness",
            "completeness",
            "instruction_following",
        ],
    )

    

    assert "4" in prompt


def test_pairwise_prompt_can_disable_verbosity_mitigation():
    prompt = build_pairwise_prompt(
        case_id="qa_001",
        user_input="What is 2 + 2?",
        system_prompt="Answer accurately.",
        candidate_a="4",
        candidate_b="The answer is four.",
        a_position="first",
        mitigation_enabled=False,
    )

    assert (
        VERBOSITY_MITIGATION_INSTRUCTIONS
        not in prompt
    )


def test_pairwise_prompt_can_enable_verbosity_mitigation():
    prompt = build_pairwise_prompt(
        case_id="qa_001",
        user_input="What is 2 + 2?",
        system_prompt="Answer accurately.",
        candidate_a="4",
        candidate_b="The answer is four.",
        a_position="first",
        mitigation_enabled=True,
    )

    assert (
        VERBOSITY_MITIGATION_INSTRUCTIONS
        in prompt
    )