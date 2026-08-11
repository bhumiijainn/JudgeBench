import json
from datetime import datetime, timezone
from pathlib import Path

from app.cost import calculate_cost


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "llm_calls.jsonl"


def log_llm_call(
    *,
    prompt: str,
    text: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    latency_ms: float,
    purpose: str,
) -> None:
    """Append one auditable LLM call to a JSONL log."""

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    estimated_cost = calculate_cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "provider": "google",
        "purpose": purpose,
        "model": model,

        "prompt": prompt,
        "raw_response": text,

        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,

        "latency_ms": round(
            latency_ms,
            2,
        ),

        "estimated_cost_usd": round(
            estimated_cost,
            8,
        ),
    }

    with LOG_FILE.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )