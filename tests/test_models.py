import pytest
from pydantic import ValidationError

from app.models import (
    CriterionScore,
    JudgeVerdict,
)


def test_valid_judge_verdict():
    verdict = JudgeVerdict(
        case_id="case_001",
        criteria=[
            CriterionScore(
                name="correctness",
                score=5,
                rationale="The response is correct.",
            )
        ],
        overall_score=5,
        passed=True,
        summary="Strong response.",
    )

    assert verdict.case_id == "case_001"
    assert verdict.passed is True


def test_score_cannot_exceed_five():
    with pytest.raises(ValidationError):
        CriterionScore(
            name="correctness",
            score=6,
            rationale="Invalid score.",
        )


def test_score_cannot_be_below_one():
    with pytest.raises(ValidationError):
        CriterionScore(
            name="correctness",
            score=0,
            rationale="Invalid score.",
        )