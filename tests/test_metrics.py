from app.loader import load_test_suite


def test_core_dataset_has_30_cases():
    cases = load_test_suite("data/test_suite.yaml")

    assert len(cases) == 30


def test_core_dataset_has_unique_ids():
    cases = load_test_suite("data/test_suite.yaml")

    ids = [case["id"] for case in cases]

    assert len(ids) == len(set(ids))


def test_every_case_has_candidates():
    cases = load_test_suite("data/test_suite.yaml")

    for case in cases:
        assert "candidate_a" in case
        assert "candidate_b" in case
        assert "output" in case["candidate_a"]
        assert "output" in case["candidate_b"]


def test_adversarial_dataset_has_10_cases():
    cases = load_test_suite("data/adversarial.yaml")

    assert len(cases) == 10


def test_adversarial_cases_have_expected_winner():
    cases = load_test_suite("data/adversarial.yaml")

    for case in cases:
        assert case["expected_winner"] in {"A", "B"}