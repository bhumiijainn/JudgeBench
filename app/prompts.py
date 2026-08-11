from app.rubric import RUBRIC


def build_judge_prompt(
    *,
    case_id: str,
    user_input: str,
    system_prompt: str,
    model_output: str,
    expected_output: str | None = None,
    criteria: list[str] | None = None,
) -> str:
    """Build a structured pointwise judging prompt."""

    selected_criteria = (
        criteria
        if criteria
        else [
            criterion.name
            for criterion in RUBRIC
        ]
    )

    rubric_text = "\n".join(
        f"- {criterion.name}: "
        f"{criterion.definition} "
        f"(weight={criterion.weight:.2f})"
        for criterion in RUBRIC
        if criterion.name in selected_criteria
    )

    reference_section = ""

    if expected_output:
        reference_section = f"""
EXPECTED OUTPUT:
{expected_output}
"""

    return f"""
You are an impartial LLM evaluator.

Evaluate the model output against the input,
system instructions, and rubric.

CASE ID:
{case_id}

SYSTEM PROMPT:
{system_prompt}

USER INPUT:
{user_input}

MODEL OUTPUT:
{model_output}
{reference_section}

RUBRIC:
{rubric_text}

SCORING SCALE:
1 = Completely unacceptable
2 = Major problems
3 = Partially acceptable
4 = Good with minor issues
5 = Excellent

JUDGING RULES:

1. Judge the actual content, not writing style alone.
2. Do not reward verbosity unless it adds useful information.
3. Do not penalize concise answers when they fully satisfy the task.
4. Ground every criterion rationale in concrete evidence.
5. Do not invent facts that are not present.
6. If an expected output is provided, use it as a reference,
   but do not blindly copy its wording.
7. Follow the rubric independently for every criterion.
8. Return ONLY valid JSON.
9. Do not wrap the JSON in markdown fences.

REQUIRED JSON STRUCTURE:

{{
  "case_id": "{case_id}",
  "criteria": [
    {{
      "name": "correctness",
      "score": 1-5,
      "rationale": "Concrete evidence..."
    }}
  ],
  "overall_score": 1-5,
  "passed": true,
  "summary": "Brief overall assessment."
}}
""".strip()