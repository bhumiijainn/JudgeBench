import json

from pydantic import ValidationError

from app.models import JudgeVerdict


class VerdictParseError(Exception):
    """Raised when a judge response cannot be parsed."""


def extract_json_object(text: str) -> str:
    """
    Extract the first JSON object from a model response.

    Handles:
    - plain JSON
    - markdown JSON fences
    - explanatory text around JSON
    """

    text = text.strip()

    # Remove markdown fences when present.
    if text.startswith("```"):
        lines = text.splitlines()

        if lines:
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

    # Fast path: response is already a JSON object.
    if text.startswith("{") and text.endswith("}"):
        return text

    # Find the first JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise VerdictParseError(
            "No JSON object found in judge response."
        )

    return text[start:end + 1]


def parse_judge_verdict(text: str) -> JudgeVerdict:
    """
    Parse and validate a judge response.
    """

    try:
        json_text = extract_json_object(text)

        data = json.loads(json_text)

        return JudgeVerdict.model_validate(data)

    except json.JSONDecodeError as exc:
        raise VerdictParseError(
            f"Invalid JSON: {exc}"
        ) from exc

    except ValidationError as exc:
        raise VerdictParseError(
            f"Invalid verdict schema: {exc}"
        ) from exc