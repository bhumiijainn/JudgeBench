from app.bias_validation import (
    calculate_overall_status,
)


def test_all_validation_sections_measured():
    sections = {
        "position_bias": {
            "status": "MEASURED",
        },
        "verbosity_bias": {
            "status": "MEASURED",
        },
        "sycophancy": {
            "status": "MEASURED",
        },
        "human_validation": {
            "status": "COMPLETE",
        },
        "test_retest": {
            "status": "COMPLETE",
        },
        "adversarial_validation": {
            "status": "MEASURED",
        },
    }

    assert (
        calculate_overall_status(
            sections
        )
        == "COMPLETE"
    )


def test_partial_validation_status():
    sections = {
        "position_bias": {
            "status": "MEASURED",
        },
        "verbosity_bias": {
            "status": "NO_DATA",
        },
        "sycophancy": {
            "status": "MITIGATION_IMPLEMENTED",
        },
        "human_validation": {
            "status": "INCOMPLETE",
        },
        "test_retest": {
            "status": "NO_DATA",
        },
        "adversarial_validation": {
            "status": "MEASURED",
        },
    }

    assert (
        calculate_overall_status(
            sections
        )
        == "PARTIAL"
    )


def test_no_empirical_data_is_incomplete():
    sections = {
        "position_bias": {
            "status": "NO_DATA",
        },
        "verbosity_bias": {
            "status": "NO_DATA",
        },
        "sycophancy": {
            "status":
                "MITIGATION_IMPLEMENTED",
        },
        "human_validation": {
            "status": "NO_DATA",
        },
        "test_retest": {
            "status": "NO_DATA",
        },
        "adversarial_validation": {
            "status": "NO_DATA",
        },
    }

    assert (
        calculate_overall_status(
            sections
        )
        == "INCOMPLETE"
    )