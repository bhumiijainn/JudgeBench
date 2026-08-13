
# JudgeBench — LLM-as-Judge Evaluation Pipeline

<p align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/Tests-66%20Passed-success?logo=pytest&logoColor=white)](https://pytest.org/)
[![LLM-as-Judge](https://img.shields.io/badge/LLM--as--Judge-Evaluation-7C3AED)](#overview)
[![Pairwise](https://img.shields.io/badge/Pairwise-A%2FB%20Evaluation-2563EB)](#judging-modes)
[![Bias Detection](https://img.shields.io/badge/Bias-Detection-F59E0B)](#bias-detection--mitigation)
[![Validation](https://img.shields.io/badge/Judge-Validation-10B981)](#judge-validation)
[![Auditability](https://img.shields.io/badge/Auditable-JSON%20Reports-0891B2)](#auditability)
[![Status](https://img.shields.io/badge/Status-Active-22C55E)](#overview)

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![YAML](https://img.shields.io/badge/Data-YAML-CB171E?logo=yaml&logoColor=white)
![JSON](https://img.shields.io/badge/Reports-JSON-000000?logo=json&logoColor=white)
![Pytest](https://img.shields.io/badge/Testing-Pytest-0A9EDC?logo=pytest&logoColor=white)
![LLM Evaluation](https://img.shields.io/badge/Focus-LLM%20Evaluation-8B5CF6)
![Position Bias](https://img.shields.io/badge/Checks-Position%20Bias-E11D48)
![Verbosity Bias](https://img.shields.io/badge/Checks-Verbosity%20Bias-F97316)

</p>

<p align="center">
  <strong>Bias-aware • Auditable • Structured • Validated</strong>
</p>

<p align="center">
  An auditable LLM-as-Judge evaluation pipeline for structured quality assessment,
  bias detection, judge validation, and A/B comparison.
</p>

---

## Overview

JudgeBench is an **LLM-as-Judge evaluation pipeline** designed to evaluate model outputs while also evaluating the reliability of the judge itself.

LLM judges can scale evaluation when human review cannot cover every model output. However, judges can introduce systematic errors such as:

- Position bias
- Verbosity / length bias
- Self-enhancement
- Sycophancy and style influence
- Score clustering

JudgeBench addresses these risks through structured judging, explicit rubrics, pairwise evaluation, adversarial testing, validation experiments, and auditable result artifacts.

The core principle is:

> **Do not trust the judge simply because the judge is a strong model.**

The evaluator must itself be evaluated.

---

# Features

- Structured LLM-as-Judge evaluation
- Pointwise evaluation
- Pairwise A/B evaluation
- Explicit multi-criterion rubric
- Robust structured-output parsing
- Malformed JSON handling
- Position-bias detection
- Verbosity-bias mitigation
- Adversarial evaluation
- Human/gold validation
- Test-retest consistency
- Judge/generator configuration separation
- Token and latency tracking
- Audit logging
- A/B comparison
- Bias-validation summary
- Final scorecard
- Automated test suite

---

# Architecture

```text
                         ┌──────────────────────┐
                         │      Test Suite      │
                         │      JSON / YAML     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Dataset Validator   │
                         │   Schema + Cases     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Judging Prompt      │
                         │      Builder         │
                         │                      │
                         │ Input + Candidates   │
                         │ + Rubric + Criteria  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Configurable      │
                         │      LLM Judge       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Raw Judge Response │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Structured Parser    │
                         │                      │
                         │ JSON validation      │
                         │ Malformed handling   │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌───────────────────┐           ┌───────────────────┐
          │    Pointwise      │           │    Pairwise A/B   │
          │    Evaluation     │           │                   │
          │                   │           │ A → B             │
          │ Criterion scores  │           │ B → A             │
          │ + rationale       │           │                   │
          └─────────┬─────────┘           └─────────┬─────────┘
                    │                               │
                    │                               ▼
                    │                    ┌───────────────────┐
                    │                    │ Position Bias     │
                    │                    │ Check             │
                    │                    │                   │
                    │                    │ Winner comparison  │
                    │                    │ Flip detection     │
                    │                    └─────────┬─────────┘
                    │                              │
                    └──────────────┬───────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │   Per-Case Results   │
                         │                      │
                         │ Scores / rationale   │
                         │ Winner / metrics     │
                         │ Tokens / latency     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Suite Aggregation   │
                         │                      │
                         │ Pass rate            │
                         │ Mean scores          │
                         │ Win rate             │
                         │ Bias metrics         │
                         │ Validation metrics   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    JSON Reports      │
                         │                      │
                         │ Audit logs           │
                         │ Bias reports         │
                         │ A/B comparison       │
                         │ Final scorecard      │
                         └──────────────────────┘
````

---

# Judging Modes

## Pointwise Evaluation

Pointwise judging evaluates an individual candidate against an explicit rubric.

It is appropriate when an absolute quality assessment is required.

```text
Candidate
    ↓
Rubric
    ↓
Criterion Scores
    ↓
Overall Score
```

The output contains per-criterion scores, rationales, an overall score, pass/fail status, and a summary.

---

## Pairwise A/B Evaluation

Pairwise judging compares two candidate responses.

```text
Candidate A
     vs
Candidate B
```

JudgeBench evaluates both candidate orders:

```text
A → B

B → A
```

The two decisions are compared to identify position sensitivity.

Pairwise evaluation is also used as an alternative to relying exclusively on absolute numerical scoring, helping address score-clustering concerns.

---

# Evaluation Rubric

JudgeBench uses an explicit rubric rather than asking the judge for a bare number.

## Correctness

Measures whether the response is factually and logically correct.

## Faithfulness

Measures whether claims remain grounded in the supplied information or reference.

## Completeness

Measures whether the response addresses the required parts of the task.

## Instruction Following

Measures whether the response follows the supplied instructions.

## Tone / Safety

Measures whether the response is appropriate and satisfies applicable safety requirements.

Each criterion receives a structured score and rationale.

---

# Structured Verdict

A typical pointwise verdict contains:

```json
{
  "criteria": [
    {
      "name": "correctness",
      "score": 5.0,
      "rationale": "The response correctly answers the question."
    },
    {
      "name": "completeness",
      "score": 5.0,
      "rationale": "The response fully addresses the requested information."
    },
    {
      "name": "instruction_following",
      "score": 5.0,
      "rationale": "The response follows the supplied instructions."
    }
  ],
  "overall_score": 5.0,
  "passed": true,
  "summary": "The response is accurate and follows the instructions."
}
```

Malformed judge responses are handled through the structured parsing and recovery layer.

---

# Bias Detection & Mitigation

JudgeBench treats judge bias as a first-class evaluation problem.

---

## Position Bias

### Problem

A judge may prefer whichever candidate appears first.

### Mitigation

Each pairwise comparison is evaluated twice:

```text
A → B
B → A
```

### Measurement

The system records:

* First-order winner
* Second-order winner
* Final winner
* Position flip
* Position-flip rate

A position flip occurs when changing candidate order changes the judge's decision.

---

## Verbosity Bias

### Problem

A judge may prefer a longer response simply because it contains more text.

### Mitigation

JudgeBench compares baseline and mitigated evaluations.

The evaluation considers whether additional content is:

* Relevant
* Supported
* Useful
* Necessary

Unsupported verbosity should not automatically improve a candidate's evaluation.

### Measurement

The verbosity experiment compares:

```text
Baseline
   ↓
Mitigated
```

using metrics such as winner changes, position flips, bias change, and accuracy change.

---

## Self-Enhancement

### Problem

A judge may favor outputs generated by its own model family.

### Mitigation

Judge and generator configuration are kept independent.

This allows the judge to be selected from a different model family when available.

The current implementation supports this mitigation, but a controlled cross-model experiment is required before claiming an empirical reduction in self-enhancement.

---

## Sycophancy / Style Influence

### Problem

A confident or persuasive answer can appear better than a correct but less persuasive answer.

### Mitigation

JudgeBench uses:

* Per-criterion grounding
* Explicit correctness evaluation
* Confidently-wrong adversarial probes

The goal is to make the judge evaluate actual response quality rather than presentation alone.

---

## Score Clustering

### Problem

Pointwise judges can concentrate scores around a narrow region of the numerical scale.

### Mitigation

JudgeBench supports pairwise evaluation as an alternative to relying exclusively on absolute pointwise scores.

Pairwise evaluation asks:

```text
Which candidate is better?
```

instead of requiring precise absolute calibration.

---

# Judge Validation

JudgeBench validates the evaluator itself using multiple approaches.

## Human / Gold Validation

The system compares judge pairwise results against human/gold labels.

Reported metrics include:

* Comparable cases
* Agreed cases
* Disagreed cases
* Agreement rate
* Cohen's kappa when statistically applicable

Cohen's kappa is not reported when the available gold labels contain only one class.

---

## Test-Retest Consistency

Test-retest evaluation measures whether the judge gives the same result when the same evaluation is repeated.

This is different from position bias.

### Position Bias

```text
Does changing A/B order change the result?
```

### Test-Retest

```text
Does repeating the same evaluation change the result?
```

The system records:

* Completed cases
* Consistent cases
* Changed cases
* Consistency rate
* Flip rate

---

## Adversarial Validation

The adversarial suite contains probes such as:

* Verbose but wrong
* Terse but correct
* Confidently wrong

The system records:

* Expected winner
* Judge winner
* Expected-winner accuracy
* Position flips

These tests provide evidence about whether the judge can resist misleading candidate characteristics.

---

# A/B Comparison

JudgeBench supports direct comparison between two configurations.

```text
Configuration A
       vs
Configuration B
```

The comparison reports:

* A wins
* B wins
* Ties
* Win rate
* Final winner
* Completion status

An incomplete experiment does not produce a misleading winner.

---

# Auditability

JudgeBench stores evaluation information for inspection and replay.

Depending on the evaluation, artifacts contain:

* Case ID
* Input
* System prompt
* Judge prompt
* Raw judge response
* Parsed verdict
* Criterion scores
* Rationales
* Winner
* Position-flip information
* Input tokens
* Output tokens
* Latency
* Model configuration

This makes the evaluation process auditable instead of treating the final score as an unexplained number.

---

# Project Structure

```text
JudgeBench/
│
├── app/
│   ├── ab_comparison.py
│   ├── adversarial_runner.py
│   ├── bias_validation.py
│   ├── cost.py
│   ├── final_scorecard.py
│   ├── judge.py
│   ├── judge_validation.py
│   ├── llm_client.py
│   ├── logger.py
│   ├── models.py
│   ├── pairwise.py
│   ├── parser.py
│   ├── prompts.py
│   ├── rubric.py
│   ├── test_retest.py
│   ├── verbosity_mitigation.py
│   ├── verbosity_report.py
│   └── verbosity_runner.py
│
├── configs/
│
├── data/
│   ├── test_suite.yaml
│   ├── adversarial.yaml
│   ├── human_labels.yaml
│   ├── verbosity.yaml
│   └── verbosity_suite.yaml
│
├── result/
│   ├── adversarial_cases.json
│   ├── adversarial_position_bias.json
│   ├── bias_validation_summary.json
│   ├── final_scorecard.json
│   ├── judge_validation.json
│   ├── verbosity_comparison.json
│   └── verbosity_report.json
│
├── tests/
│
├── .env.example
├── .gitignore
├── DISCUSSION.md
├── main.py
├── pytest.ini
├── README.md
└── requirements.txt
```

---

# Installation

## Requirements

* Python 3.11+
* Git
* Internet connection
* API access to the configured LLM provider

## Clone the Repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd JudgeBench
```

## Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here

JUDGE_MODEL=your_judge_model
GENERATOR_MODEL=your_generator_model

JUDGE_TEMPERATURE=0
GENERATOR_TEMPERATURE=0.2

PASS_THRESHOLD=3.5
```

**Never commit `.env` or real API credentials to Git.**

A safe `.env.example` file is included in the repository.

---

# Quick Start

## Validate Dataset

```powershell
python main.py validate-dataset
```

## Validate Adversarial Dataset

```powershell
python main.py validate-adversarial
```

## Run Pointwise Evaluation

```powershell
python main.py judge-one qa_001
```

## Run Pairwise Evaluation

```powershell
python main.py pairwise-one qa_001
```

## Run Adversarial Evaluation

```powershell
python main.py run-adversarial
```

## Run Verbosity Evaluation

```powershell
python main.py run-verbosity baseline
python main.py run-verbosity mitigated
python main.py compare-verbosity
python main.py report-verbosity
```

## Run Human / Gold Validation

```powershell
python main.py validate-judge
```

## Run Test-Retest Validation

```powershell
python main.py test-retest
```

## Generate A/B Comparison

```powershell
python main.py compare-ab
```

## Generate Bias Validation

```powershell
python main.py validate-bias
```

## Generate Final Scorecard

```powershell
python main.py scorecard
```

---

# Testing

Run the complete automated test suite:

```powershell
pytest -v
```

Current development result:

```text
66 passed
```

The test suite covers:

* Dataset validation
* Model configuration
* Prompt construction
* Structured parsing
* Rubric validation
* Pointwise judging
* Pairwise judging
* Position-bias logic
* Bias validation
* Verbosity mitigation
* Verbosity reporting
* Adversarial evaluation
* Human/gold validation
* Test-retest logic
* A/B comparison
* Experiment integrity
* Benchmark quality

---

# Result Artifacts

Important generated artifacts include:

```text
result/
├── adversarial_cases.json
├── adversarial_position_bias.json
├── bias_validation_summary.json
├── final_scorecard.json
├── judge_validation.json
├── qa_001.json
├── qa_001_pairwise.json
├── verbosity_bias.json
├── verbosity_comparison.json
└── verbosity_report.json
```

These files provide machine-readable evidence from the evaluation experiments.

---

# Limitations

JudgeBench is an evaluation framework, not proof that an LLM judge is unbiased.

Important limitations include:

1. Human/gold validation depends on the quality and diversity of available labels.
2. A small validation sample cannot establish universal judge reliability.
3. Adversarial probes only test the behaviors represented by the benchmark.
4. Self-enhancement requires controlled cross-model experiments for strong empirical conclusions.
5. Pairwise evaluation provides an alternative to absolute score calibration but is not a complete statistical calibration study.
6. API availability and model stochasticity can affect repeated experiments.
7. Results from one judge model should not automatically be generalized to other judge models.

---

# Release-Gating Recommendation

JudgeBench should **not be used as the sole release gate for high-impact production changes**.

A safer process is:

```text
Automated Tests
      +
LLM Judge
      +
Adversarial Evaluation
      +
Bias Validation
      +
Human Review
```

For lower-risk changes, an LLM judge can provide a useful automated evaluation signal.

For high-risk changes, the judge should remain one component of the decision rather than the only approval mechanism.

The fundamental reason is simple:

> The judge is itself a model and can therefore introduce systematic evaluation errors.

---

# Design Principle

The central principle behind JudgeBench is:

> **Do not trust the judge simply because the judge is a strong model.**

The evaluator must itself be evaluated.

JudgeBench therefore measures both:

```text
Candidate Quality
```

and:

```text
Evaluator Reliability
```

This makes the system suitable for studying the reliability of LLM-based evaluation pipelines rather than treating an LLM judge as ground truth.

---

# Author

**Bhumi Jain**

B.Tech — Artificial Intelligence & Data Science

JudgeBench — LLM-as-Judge Evaluation Pipeline

---

<p align="center">

**Built with Python • LLM Evaluation • Bias Analysis • Structured Judging**

</p>
```

⭐ **If you find this project useful, consider starring the repository.**

