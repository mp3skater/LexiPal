import re
from typing import List, Dict, Tuple

from utils.llm_api.gemini_api.gemini_api import ask_gemini  # Ensure this import is correct


def _extract_prompt_from_response(text: str) -> str:
    """Extract prompt from XML-like tags with robust fallback."""
    match = re.search(r"<PROMPT>(.*?)</PROMPT>", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def _extract_score_from_response(text: str) -> float:
    """Extract score with XML tag priority and numerical fallback."""
    score_match = re.search(r"<SCORE>(.*?)</SCORE>", text, re.DOTALL)
    if score_match:
        text = score_match.group(1)
    num_match = re.search(r"(\d+\.?\d*)", text)

    return min(max(float(num_match.group(1)), 0.0) if num_match else 0.0, 10.0)


class PromptOptimizer:
    def __init__(self, api_key: str, criteria: List[Dict], max_iterations: int = 5,
                 score_threshold: float = 8.0):
        self.api_key = api_key
        self.criteria = criteria
        self.max_iterations = max_iterations
        self.score_threshold = score_threshold
        self.score_history = []

    def optimize_prompt(self, initial_prompt: str) -> Tuple[str, float]:
        current_prompt = initial_prompt
        best_score = 0.0
        best_prompt = current_prompt

        for iteration in range(self.max_iterations):
            # Generate response from current prompt
            response = ask_gemini(current_prompt, self.api_key)

            # Get combined evaluation and improvement
            score, new_prompt = self._evaluate_and_improve(current_prompt, response)
            self.score_history.append(score)

            # Update best results if current is better
            if score > best_score:
                best_score = score
                best_prompt = current_prompt

            # Early stopping condition
            if score >= self.score_threshold:
                break

            current_prompt = new_prompt

        return best_prompt, best_score

    def _evaluate_and_improve(self, current_prompt: str, response: str) -> Tuple[float, str]:
        """Combined evaluation and improvement in one API call."""
        criteria_formatted = "\n".join(
            f"- {c['name']} (Weight: {c.get('weight', 1.0)}): {c['description']}"
            for c in self.criteria
        )

        evaluation_prompt = f"""
        Analyze this prompt-response pair and provide both a score and improved prompt:

        [Original Prompt]
        {current_prompt}

        [Generated Response]
        {response}

        [Evaluation Criteria]
        {criteria_formatted}

        Perform these tasks:
        1. Evaluate response quality against criteria using weighted average
        2. Score between 0-10 (considering all criteria weights)
        3. Create improved prompt addressing weaknesses
        4. Format strictly as:
           <SCORE>score</SCORE>
           <PROMPT>improved_prompt</PROMPT>

        Provide only the XML-formatted response.
        """

        api_response = ask_gemini(evaluation_prompt, self.api_key)
        return (
            _extract_score_from_response(api_response),
            _extract_prompt_from_response(api_response)
        )
