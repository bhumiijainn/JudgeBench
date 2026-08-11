from app.pairwise import PairwiseResult


def test_no_position_flip():
    result = PairwiseResult(
        case_id="qa_001",
        first_order_winner="A",
        second_order_winner="A",
        final_winner="A",
        position_flip=False,
        first_order_reason="A is better.",
        second_order_reason="A is better.",
        first_order_latency_ms=100,
        second_order_latency_ms=110,
        first_order_input_tokens=100,
        first_order_output_tokens=50,
        second_order_input_tokens=100,
        second_order_output_tokens=50,
    )

    assert result.position_flip is False
    assert result.first_order_winner == "A"
    assert result.second_order_winner == "A"
    assert result.final_winner == "A"


def test_position_flip_is_detected():
    result = PairwiseResult(
        case_id="qa_002",
        first_order_winner="A",
        second_order_winner="B",
        final_winner="tie",
        position_flip=True,
        first_order_reason="A wins.",
        second_order_reason="B wins.",
        first_order_latency_ms=100,
        second_order_latency_ms=110,
        first_order_input_tokens=100,
        first_order_output_tokens=50,
        second_order_input_tokens=100,
        second_order_output_tokens=50,
    )

    assert result.position_flip is True
    assert result.first_order_winner != result.second_order_winner
    assert result.final_winner == "tie"


def test_position_flip_result_preserves_both_reasons():
    result = PairwiseResult(
        case_id="qa_003",
        first_order_winner="A",
        second_order_winner="B",
        final_winner="tie",
        position_flip=True,
        first_order_reason="Response A is more concise.",
        second_order_reason="Response B is more concise.",
        first_order_latency_ms=120,
        second_order_latency_ms=130,
        first_order_input_tokens=120,
        first_order_output_tokens=60,
        second_order_input_tokens=120,
        second_order_output_tokens=60,
    )

    assert result.first_order_reason
    assert result.second_order_reason

    assert (
        result.first_order_reason
        != result.second_order_reason
    )


def test_stable_winner_is_not_a_position_flip():
    result = PairwiseResult(
        case_id="qa_004",
        first_order_winner="B",
        second_order_winner="B",
        final_winner="B",
        position_flip=False,
        first_order_reason="B is more complete.",
        second_order_reason="B is more complete.",
        first_order_latency_ms=100,
        second_order_latency_ms=100,
        first_order_input_tokens=100,
        first_order_output_tokens=50,
        second_order_input_tokens=100,
        second_order_output_tokens=50,
    )

    assert result.position_flip is False
    assert result.final_winner == "B"