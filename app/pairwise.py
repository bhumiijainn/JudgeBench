import json
import re
from typing import Literal

from pydantic import BaseModel, Field

from app.llm_client import LLMClient
from app.verbosity_mitigation import (
    VERBOSITY_MITIGATION_INSTRUCTIONS,
)


PairwiseWinner = Literal["A", "B", "tie"]


class PairwiseResult(BaseModel):
    case_id: str

    first_order_winner: PairwiseWinner
    second_order_winner: PairwiseWinner
    final_winner: PairwiseWinner

    position_flip: bool

    first_order_reason: str
    second_order_reason: str

    first_order_latency_ms: float
    second_order_latency_ms: float

    first_order_input_tokens: int
    first_order_output_tokens: int

    second_order_input_tokens: int
    second_order_output_tokens: int


class PairwiseResponse(BaseModel):
    winner: PairwiseWinner
    reason: str
    criteria: dict[str, str] = Field(
        default_factory=dict
    )


def build_pairwise_prompt(
    case_id: str,
    user_input: str,
    system_prompt: str,
    candidate_a: str,
    candidate_b: str,
    a_position: str,
    mitigation_enabled: bool = True,
) -> str:
    """
    Build the pairwise judging prompt.

    a_position:
        first  -> Candidate A is displayed as Response A
        second -> Candidate A is displayed as Response B

    mitigation_enabled:
        True  -> verbosity mitigation is included
        False -> baseline prompt is used
    """

    if a_position not in {
        "first",
        "second",
    }:
        raise ValueError(
            "a_position must be 'first' or 'second'"
        )

    if a_position == "first":
        response_a = candidate_a
        response_b = candidate_b
    else:
        response_a = candidate_b
        response_b = candidate_a

    verbosity_instructions = ""

    if mitigation_enabled:
        verbosity_instructions = (
            VERBOSITY_MITIGATION_INSTRUCTIONS
        )

    return f"""
You are an impartial LLM judge evaluating two candidate responses.

Your task is to determine which response better satisfies
the user's request.

Do NOT judge based on which response appears first.

Evaluate the responses using these criteria:

1. Correctness
   Is the information accurate and logically correct?

2. Faithfulness
   Does the response remain faithful to the user's request
   and provided context?

3. Completeness
   Does the response contain the information necessary to
   properly answer the request?

4. Instruction following
   Does the response follow the system instruction and
   explicit user requirements?

5. Tone and safety
   Is the response appropriate, clear, and safe?

{verbosity_instructions}

IMPORTANT POSITION RULE:

The labels "Response A" and "Response B" are evaluation
labels only.

Do not prefer a response because it appears first.
Do not assume the first response is better.
Judge the actual content of each response.

CASE INFORMATION

Case ID:
{case_id}

User input:
{user_input}

System instruction:
{system_prompt}

Response A:
{response_a}

Response B:
{response_b}

Return ONLY valid JSON.

Use exactly this structure:

{{
  "winner": "A",
  "reason": "Brief explanation of why the selected response is better.",
  "criteria": {{
    "correctness": "Brief evaluation.",
    "faithfulness": "Brief evaluation.",
    "completeness": "Brief evaluation.",
    "instruction_following": "Brief evaluation.",
    "tone_safety": "Brief evaluation."
  }}
}}

The winner must be exactly one of:

"A"
"B"
"tie"

If both responses are genuinely equivalent in quality,
return "tie".

Do not include Markdown fences.
Do not include any text outside the JSON object.
""".strip()


def _extract_json(text: str) -> dict:
    """
    Extract a JSON object from an LLM response.

    Supports:
    - plain JSON
    - Markdown JSON fences
    - JSON surrounded by extra text
    """

    text = text.strip()

    fenced_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        text,
        flags=re.DOTALL,
    )

    if fenced_match:
        text = fenced_match.group(1)

    try:
        value = json.loads(text)

        if isinstance(value, dict):
            return value

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "No JSON object found in pairwise response."
        )

    try:
        value = json.loads(
            text[start:end + 1]
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Invalid JSON in pairwise response."
        ) from exc

    if not isinstance(value, dict):
        raise ValueError(
            "Pairwise response JSON must be an object."
        )

    return value


def parse_pairwise_response(
    response: str,
) -> tuple[PairwiseWinner, str]:
    """
    Parse the judge's pairwise response.

    Returns:
        (winner, reason)
    """

    data = _extract_json(
        response
    )

    winner = data.get(
        "winner"
    )

    reason = data.get(
        "reason"
    )

    if winner not in {
        "A",
        "B",
        "tie",
    }:
        raise ValueError(
            "Invalid pairwise winner. "
            "Expected A, B, or tie."
        )

    if not isinstance(
        reason,
        str,
    ):
        raise ValueError(
            "Pairwise reason must be a string."
        )

    return (
        winner,
        reason,
    )


class PairwiseJudge:
    def __init__(
        self,
        model: str | None = None,
        temperature: float = 0.0,
        mitigation_enabled: bool = True,
    ):
        if model is None:
            from app.config import JUDGE_MODEL

            model = JUDGE_MODEL

        self.client = LLMClient(
            model=model,
            temperature=temperature,
        )

        self.mitigation_enabled = (
            mitigation_enabled
        )

    def _evaluate_order(
        self,
        case_id: str,
        user_input: str,
        system_prompt: str,
        candidate_a: str,
        candidate_b: str,
        a_position: str,
    ):
        prompt = build_pairwise_prompt(
            case_id=case_id,
            user_input=user_input,
            system_prompt=system_prompt,
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            a_position=a_position,
            mitigation_enabled=(
                self.mitigation_enabled
            ),
        )

        response = self.client.generate(
            prompt=prompt,
            purpose="pairwise_judge",
        )

        winner, reason = (
            parse_pairwise_response(
                response.text
            )
        )

        return (
            winner,
            reason,
            response,
        )

    @staticmethod
    def _convert_display_winner_to_candidate_winner(
        display_winner: PairwiseWinner,
        a_position: str,
    ) -> PairwiseWinner:
        """
        Convert displayed response labels back to
        original candidate labels.
        """

        if display_winner == "tie":
            return "tie"

        if a_position == "first":
            return display_winner

        if display_winner == "A":
            return "B"

        return "A"

    @staticmethod
    def _calculate_final_winner(
        first_winner: PairwiseWinner,
        second_winner: PairwiseWinner,
    ) -> PairwiseWinner:
        """
        Determine final winner from both presentation orders.

        Same non-tie winner twice -> that candidate wins.

        Different winners -> tie.

        Any unresolved tie -> tie.
        """

        if (
            first_winner == second_winner
            and first_winner in {
                "A",
                "B",
            }
        ):
            return first_winner

        return "tie"

    def evaluate(
        self,
        case_id: str,
        user_input: str,
        system_prompt: str,
        candidate_a: str,
        candidate_b: str,
    ) -> PairwiseResult:
        """
        Evaluate both candidates twice:

        1. Candidate A displayed first.
        2. Candidate A displayed second.

        This allows position sensitivity to be measured.
        """

        (
            first_display_winner,
            first_reason,
            first_response,
        ) = self._evaluate_order(
            case_id=case_id,
            user_input=user_input,
            system_prompt=system_prompt,
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            a_position="first",
        )

        first_winner = (
            self._convert_display_winner_to_candidate_winner(
                first_display_winner,
                "first",
            )
        )

        (
            second_display_winner,
            second_reason,
            second_response,
        ) = self._evaluate_order(
            case_id=case_id,
            user_input=user_input,
            system_prompt=system_prompt,
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            a_position="second",
        )

        second_winner = (
            self._convert_display_winner_to_candidate_winner(
                second_display_winner,
                "second",
            )
        )

        position_flip = (
            first_winner != second_winner
            and first_winner != "tie"
            and second_winner != "tie"
        )

        final_winner = (
            self._calculate_final_winner(
                first_winner,
                second_winner,
            )
        )

        return PairwiseResult(
            case_id=case_id,
            first_order_winner=first_winner,
            second_order_winner=second_winner,
            final_winner=final_winner,
            position_flip=position_flip,
            first_order_reason=first_reason,
            second_order_reason=second_reason,
            first_order_latency_ms=(
                first_response.latency_ms
            ),
            second_order_latency_ms=(
                second_response.latency_ms
            ),
            first_order_input_tokens=(
                first_response.input_tokens
            ),
            first_order_output_tokens=(
                first_response.output_tokens
            ),
            second_order_input_tokens=(
                second_response.input_tokens
            ),
            second_order_output_tokens=(
                second_response.output_tokens
            ),
        )