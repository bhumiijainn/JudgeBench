from app.judge import Judge


def test_judge_can_be_constructed_without_api_call(
    monkeypatch,
):
    monkeypatch.setattr(
        "app.judge.LLMClient",
        lambda model, temperature: None,
    )

    judge = Judge(
        model="test-model",
        temperature=0,
    )

    assert judge.client is None