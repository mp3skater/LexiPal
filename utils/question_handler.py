from utils.gemini_api import ask_gemini
import re


def format_prompt(questions: list[str]) -> str:
    numbered_questions = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(questions)])
    return (
        f"Answer these questions sequentially using format [1] answer [2] answer...\n"
        f"{numbered_questions}\n"
        "Put only one answer per [number], be concise, use only the format."
    )


def ask_questions(questions: list[str], api_key: str) -> tuple[list[str], str]:
    prompt = format_prompt(questions)
    response = ask_gemini(prompt, api_key)
    return extract_answers(response, len(questions)), response


def extract_answers(response: str, expected_answers: int) -> list[str]:
    matches = re.findall(r'\[\d+\]\s*(.*?)(?=\s*\[\d+\]|$)', response, re.DOTALL)
    answers = [m.strip() for m in matches][:expected_answers]

    # Pad with empty strings if missing answers
    while len(answers) < expected_answers:
        answers.append("")
    return answers
