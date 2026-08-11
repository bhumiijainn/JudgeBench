import os

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    """Return a required environment variable."""
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Required environment variable '{name}' is not configured."
        )

    return value


def get_env(name: str, default: str | None = None) -> str | None:
    """Return an optional environment variable."""
    return os.getenv(name, default)


GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")

JUDGE_MODEL = get_required_env("JUDGE_MODEL")
GENERATOR_MODEL = get_required_env("GENERATOR_MODEL")

JUDGE_TEMPERATURE = float(
    get_env("JUDGE_TEMPERATURE", "0")
)

GENERATOR_TEMPERATURE = float(
    get_env("GENERATOR_TEMPERATURE", "0.2")
)

PASS_THRESHOLD = float(
    get_env("PASS_THRESHOLD", "3.5")
)