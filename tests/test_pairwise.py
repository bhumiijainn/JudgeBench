import pytest

from app.pairwise import (
    PairwiseJudge,
    PairwiseResult,
    build_pairwise_prompt,
    parse_pairwise_response,
)


def test_pairwise_prompt_contains_both_candidates():
    prompt = build_pairwise_prompt(
        case_id="qa_001",
        user_input="What is 2 + 2?",
        system_prompt="Answer accurately.",
        candidate_a="4",
        candidate_b="The answer is four.",
        a_position="first",
    )

    assert "4" in prompt
    assert "The answer is four." in prompt
    assert "qa_001" in prompt


def test_pairwise_prompt_can_reverse_position():
    prompt = build_pairwise_prompt(
        case_id="qa_001",
        user_input="What is 2 + 2?",
        system_prompt="Answer accurately.",
        candidate_a="4",
        candidate_b="The answer is four.",
        a_position="second",
    )

    assert "Response B:" in prompt
    assert "Response A:" in prompt


def test_parse_pairwise_response():
    response = """
{
  "winner": "A",
  "reason": "A is more accurate.",
  "criteria": {
    "correctness": "A is correct.",
    "faithfulness": "Both are faithful.",
    "completeness": "A is sufficient.",
    "instruction_following": "A follows the instruction.",
    "tone_safety": "Both are safe."
  }
}
"""

    winner, reason = parse_pairwise_response(
        response
    )

    assert winner == "A"
    assert reason == "A is more accurate."


def test_parse_pairwise_markdown_response():
    response = """
```json
{
  "winner": "B",
  "reason": "B is more complete."
}
"""
def test_invalid_pairwise_winner():
        response = """
{
"winner": "C",
"reason": "Invalid winner."
}
"""


def test_position_flip_detection():
        result = PairwiseResult(
case_id="qa_001",
first_order_winner="A",
second_order_winner="B",
final_winner="tie",
position_flip=True,
first_order_reason="A wins.",
second_order_reason="B wins.",
first_order_latency_ms=100,
second_order_latency_ms=110,
first_order_input_tokens=100,
first_order_output_tokens=50,
second_order_input_tokens=100,
second_order_output_tokens=50,
)
def test_judge_can_be_constructed_without_api_call(
monkeypatch,
):
        monkeypatch.setattr(
"app.pairwise.LLMClient",
lambda model, temperature: None,
)
