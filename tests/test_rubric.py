from app.rubric import (
    RUBRIC,
    rubric_total_weight,
)


def test_rubric_has_five_criteria():
    assert len(RUBRIC) == 5


def test_rubric_weights_sum_to_one():
    assert rubric_total_weight() == 1.0


def test_rubric_contains_required_criteria():
    names = {
        criterion.name
        for criterion in RUBRIC
    }

    assert "correctness" in names
    assert "faithfulness" in names
    assert "completeness" in names
    assert "instruction_following" in names
    assert "tone_safety" in names