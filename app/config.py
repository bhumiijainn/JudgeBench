import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


OPENAI_API_KEY = get_env("OPENAI_API_KEY")

JUDGE_MODEL = get_env("JUDGE_MODEL", "")
GENERATOR_MODEL = get_env("GENERATOR_MODEL", "")

JUDGE_TEMPERATURE = float(get_env("JUDGE_TEMPERATURE", "0"))
GENERATOR_TEMPERATURE = float(get_env("GENERATOR_TEMPERATURE", "0.2"))

PASS_THRESHOLD = float(get_env("PASS_THRESHOLD", "3.5"))