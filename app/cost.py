from dataclasses import dataclass


@dataclass(frozen=True)
class ModelPricing:
    """Price per 1 million tokens."""

    input_per_million: float
    output_per_million: float


# Gemini 3.6 Flash standard paid pricing.
# Free-tier usage still reports an estimated cost of $0
# when FREE_TIER is enabled in configuration.
DEFAULT_PRICING = ModelPricing(
    input_per_million=1.50,
    output_per_million=7.50,
)


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    pricing: ModelPricing = DEFAULT_PRICING,
) -> float:
    """Calculate estimated USD cost from token usage."""

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing.input_per_million

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing.output_per_million

    return input_cost + output_cost