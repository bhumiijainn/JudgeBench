from app.config import (
    JUDGE_MODEL,
    JUDGE_TEMPERATURE,
)
from app.llm_client import LLMClient
from app.models import JudgeVerdict
from app.parser import (
    VerdictParseError,
    parse_judge_verdict,
)
from app.prompts import build_judge_prompt


class Judge:
    """Pointwise LLM evaluator."""

    def __init__(
        self,
        model: str = JUDGE_MODEL,
        temperature: float = JUDGE_TEMPERATURE,
    ):
        self.client = LLMClient(
            model=model,
            temperature=temperature,
        )

    def evaluate(
        self,
        *,
        case_id: str,
        user_input: str,
        system_prompt: str,
        model_output: str,
        expected_output: str | None = None,
        criteria: list[str] | None = None,
    ) -> JudgeVerdict:
        """
        Evaluate one model output using the configured judge.
        """

        prompt = build_judge_prompt(
            case_id=case_id,
            user_input=user_input,
            system_prompt=system_prompt,
            model_output=model_output,
            expected_output=expected_output,
            criteria=criteria,
        )

        response = self.client.generate(
            prompt=prompt,
            purpose="judge",
        )

        try:
            return parse_judge_verdict(
                response.text
            )

        except VerdictParseError:
            raise