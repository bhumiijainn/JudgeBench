# JudgeBench — LLM-as-Judge Evaluation Pipeline

JudgeBench is an auditable evaluation pipeline for using an LLM as a judge of model outputs.

The project treats the judge itself as an imperfect evaluation system and explicitly measures several sources of judge bias, including position bias, verbosity bias, self-enhancement, sycophancy/style influence, and score clustering.

## 1. Problem

LLM-based judges can scale evaluation beyond human review, but the judge may introduce systematic errors.

Examples include:

- preferring the first answer presented
- preferring longer answers
- preferring outputs from its own model family
- being influenced by confident or persuasive wording
- clustering pointwise scores around a narrow range

JudgeBench evaluates these risks rather than assuming that an LLM judge is automatically reliable.

## 2. Objective

Given a test case containing:

- input
- system prompt
- candidate model output
- optional expected output
- evaluation criteria

JudgeBench produces a structured quality verdict.

The system supports:

- pointwise evaluation
- pairwise A-vs-B evaluation
- structured rubrics
- robust JSON parsing
- audit logging
- token/call tracking
- bias experiments
- validation against human/gold labels
- test-retest consistency
- A/B comparison

## 3. Architecture

```text
Test Suite
    |
    v
Dataset Loader
    |
    +----------------------+
    |                      |
    v                      v
Pointwise Judge       Pairwise Judge
    |                      |
    v                      v
Structured Verdict    A/B Verdict
    |                      |
    +----------+-----------+
               |
               v
        Result / Audit Files
               |
       +-------+-------+
       |       |       |
       v       v       v
   Bias     Validation Reports
   Tests
       |       |
       +-------+
           |
           v
      Final Scorecard     

## 4. Installation

### Requirements

- Python 3.11+
- Git
- An API key for the configured LLM provider

### Clone the repository

```bash
git clone <your-repository-url>
cd JudgeBench


Create a virtual environment
Windows
python -m venv .venv
.venv\Scripts\Activate.ps1
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
Install dependencies
pip install -r requirements.txt
Configure environment variables

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

Do not commit API keys or other secrets to Git.

Verify the installation

Run:

python main.py

You should see the available JudgeBench commands.

Run the automated tests:

pytest -v

## 5. Quick Start

Validate the datasets:

```bash
python main.py validate-dataset
python main.py validate-adversarial

Run the automated tests:

pytest -v

Run a pointwise evaluation:

python main.py judge-one qa_001

Run a pairwise evaluation:

python main.py pairwise-one qa_001

Generate the bias validation summary:

python main.py validate-bias

Generate the A/B comparison:

python main.py compare-ab

Generate the final scorecard:

python main.py scorecard