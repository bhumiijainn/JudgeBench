from google import genai
import time
from dataclasses import dataclass


from app.config import (
    GEMINI_API_KEY,
    get_required_env,
)
from app.logger import log_llm_call


@dataclass
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: float
    model: str


class LLMClient:
    """Reusable Gemini client for generator and judge calls."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
    ):
        api_key = (
            GEMINI_API_KEY
            or get_required_env(
                "GEMINI_API_KEY"
            )
        )

        self.model = model
        self.temperature = temperature

        self.client = genai.Client(
            api_key=api_key,
            http_options={
                "api_version": "v1"
            },
        )

    def generate(
        self,
        prompt: str,
        purpose: str = "unknown",
    ) -> LLMResponse:
        """Send a prompt and return response, usage, and latency."""

        start_time = time.perf_counter()

        interaction = self.client.interactions.create(
            model=self.model,
            input=prompt,
            store=False,
            generation_config={
                "temperature": self.temperature,
            },
        )

        latency_ms = (
            time.perf_counter() - start_time
        ) * 1000

        usage = getattr(
            interaction,
            "usage",
            None,
        )

        input_tokens = 0
        output_tokens = 0
        total_tokens = 0

        if usage:
            input_tokens = getattr(
                usage,
                "total_input_tokens",
                0,
            ) or 0

            output_tokens = getattr(
                usage,
                "total_output_tokens",
                0,
            ) or 0

            total_tokens = getattr(
                usage,
                "total_tokens",
                0,
            ) or 0

        if total_tokens == 0:
            total_tokens = (
                input_tokens
                + output_tokens
            )

        result = LLMResponse(
            text=interaction.output_text or "",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            model=self.model,
        )

        log_llm_call(
            prompt=prompt,
            text=result.text,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            total_tokens=result.total_tokens,
            latency_ms=result.latency_ms,
            purpose=purpose,
        )

        return result