import os
import pytest
from utils.llm_api.multiple_questions_handler.question_handler import ask_questions

API_KEY = os.getenv("GEMINI_API")

TEST_CASES = [
    {
        "questions": [
            "What is the capital of France?",
            "Current French president?",
            "National dish of France?"
        ],
        "desc": "French Culture Questions"
    },
    {
        "questions": [
            "Chemical symbol for gold?",
            "Atomic number of oxygen?",
            "Discoverer of penicillin?"
        ],
        "desc": "Science Questions"
    }
]


def run_test_case(questions, desc):
    print(f"\n{'=' * 40}")
    print(f"Test Case: {desc}")
    print(f"{'-' * 40}")

    answers, raw_response = ask_questions(questions, API_KEY)

    # Automatic validation
    assert len(answers) == len(questions), \
        f"Expected {len(questions)} answers, got {len(answers)}"

    # Show original response for debugging
    print(f"Original Gemini Response:\n{raw_response}\n")
    print("Extracted Answers:")

    # Manual verification display
    for i, (q, a) in enumerate(zip(questions, answers)):
        print(f"[Q{i + 1}] {q}")
        print(f"[A{i + 1}] {a}\n")

    return True


def test_question_answering():
    for case in TEST_CASES:
        assert run_test_case(case["questions"], case["desc"])


if __name__ == "__main__":
    pytest.main(["-s", __file__])
