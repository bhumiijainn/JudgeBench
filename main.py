from app.config import JUDGE_MODEL, GENERATOR_MODEL


def main():
    print("JudgeBench")
    print("-" * 40)
    print(f"Judge model: {JUDGE_MODEL or 'not configured'}")
    print(f"Generator model: {GENERATOR_MODEL or 'not configured'}")
    print("Environment: OK")


if __name__ == "__main__":
    main()