from typing import Literal

from pydantic import BaseModel, Field


class CriterionScore(BaseModel):
    """Score assigned to one evaluation criterion."""

    name: str

    score: float = Field(
        ge=1.0,
        le=5.0,
    )

    rationale: str = Field(
        min_length=1,
    )


class JudgeVerdict(BaseModel):
    """Structured verdict returned by the LLM judge."""

    case_id: str

    criteria: list[CriterionScore]

    overall_score: float = Field(
        ge=1.0,
        le=5.0,
    )

    passed: bool

    summary: str = Field(
        min_length=1,
    )