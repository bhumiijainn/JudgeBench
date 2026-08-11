from dataclasses import dataclass


@dataclass(frozen=True)
class RubricCriterion:
    name: str
    definition: str
    weight: float


RUBRIC = [
    RubricCriterion(
        name="correctness",
        definition=(
            "The response is factually correct and "
            "does not contain substantive errors."
        ),
        weight=0.30,
    ),
    RubricCriterion(
        name="faithfulness",
        definition=(
            "The response is supported by the provided "
            "information and does not invent unsupported claims."
        ),
        weight=0.20,
    ),
    RubricCriterion(
        name="completeness",
        definition=(
            "The response addresses the important parts "
            "of the input without omitting required information."
        ),
        weight=0.20,
    ),
    RubricCriterion(
        name="instruction_following",
        definition=(
            "The response follows the explicit instructions "
            "and requested format."
        ),
        weight=0.15,
    ),
    RubricCriterion(
        name="tone_safety",
        definition=(
            "The response uses an appropriate tone and "
            "does not introduce unsafe or inappropriate content."
        ),
        weight=0.15,
    ),
]


def rubric_total_weight() -> float:
    return sum(
        criterion.weight
        for criterion in RUBRIC
    )