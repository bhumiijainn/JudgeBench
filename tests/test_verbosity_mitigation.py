from app.verbosity_mitigation import (
    VERBOSITY_MITIGATION_INSTRUCTIONS,
)


def test_verbosity_mitigation_mentions_length():
    prompt = VERBOSITY_MITIGATION_INSTRUCTIONS.lower()

    assert "longer" in prompt
    assert "shorter" in prompt
    assert "length" in prompt


def test_verbosity_mitigation_does_not_prefer_short_answers():
    prompt = VERBOSITY_MITIGATION_INSTRUCTIONS.lower()

    assert (
        "a longer response is not inherently better"
        in prompt
    )

    assert (
        "a shorter response is not inherently better"
        in prompt
    )


def test_verbosity_mitigation_handles_user_requested_detail():
    prompt = VERBOSITY_MITIGATION_INSTRUCTIONS.lower()

    assert (
        "explicitly requests detail"
        in prompt
    )


def test_verbosity_mitigation_penalizes_irrelevant_detail():
    prompt = VERBOSITY_MITIGATION_INSTRUCTIONS.lower()

    assert (
        "irrelevant"
        in prompt
    )

    assert (
        "redundant"
        in prompt
    )