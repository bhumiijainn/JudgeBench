import sys

from app.loader import load_test_suite


def main():
    if len(sys.argv) < 2:
        print("JudgeBench")
        print("-" * 40)
        print("Usage:")
        print("  python main.py validate-dataset")
        return

    command = sys.argv[1]

    if command == "validate-dataset":
        cases = load_test_suite("data/test_suite.yaml")

        print("JudgeBench Dataset Validation")
        print("-" * 40)
        print(f"Cases loaded: {len(cases)}")

        categories = {}

        for case in cases:
            category = case.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1

        print("\nCategories:")

        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")

        print("\nDataset validation: PASSED")
    
    elif command == "validate-adversarial":
        
        cases = load_test_suite("data/adversarial.yaml")

        print("JudgeBench Adversarial Dataset")
        print("-" * 40)
        print(f"Cases loaded: {len(cases)}")
        print("Dataset validation: PASSED")
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()