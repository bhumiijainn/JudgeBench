import pytest

from app.parser import (
    VerdictParseError,
    parse_judge_verdict,
)


VALID_JSON = """
{
  "case_id": "case_001",
  "criteria": [
    {
      "name": "correctness",
      "score": 5,
      "rationale": "The answer is correct."
    }
  ],
  "overall_score": 5,
  "passed": true,
  "summary": "Excellent response."
}
"""


def test_parse_valid_json():
    verdict = parse_judge_verdict(
        VALID_JSON
    )

    assert verdict.case_id == "case_001"
    assert verdict.overall_score == 5
    assert verdict.passed is True


def test_parse_markdown_json():
    response = f""""""

{VALID_JSON}
def test_parse_json_with_extra_text():
    response = f""""""


{VALID_JSON}


"""

def test_invalid_json_raises_error():
    with pytest.raises(
VerdictParseError
):
        
        
        parse_judge_verdict(
'{"case_id": "broken"'
)

def test_invalid_schema_raises_error():
    response = """
{
"case_id": "case_001",
"criteria": [],
"overall_score": 9,
"passed": True,
"summary": "Invalid score."
}