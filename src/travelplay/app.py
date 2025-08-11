import argparse
from .llm_client import call_llm_json


def main():
    parser = argparse.ArgumentParser(description="Generate a kid travel worksheet (JSON).")
    parser.add_argument("--age", type=int, required=True)
    parser.add_argument("--destination", type=str, required=True)
    args = parser.parse_args()

    ws = call_llm_json(age=args.age, destination=args.destination)
    print(ws.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
