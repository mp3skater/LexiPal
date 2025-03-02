import re
from typing import List, Dict, Tuple

from utils.llm_api.gemini_api.gemini_api import ask_gemini


def _extract_prompt_from_response(text: str) -> str:
    """Extract prompt from XML-like tags."""
    match = re.search(r"<PROMPT>(.*?)</PROMPT>", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def _extract_score_from_response(text: str) -> float:
    match = re.search(r"(\d+\.?\d*)", text)
    if match:
        return min(max(float(match.group(1)), 0.0), 10.0)
    return 0.0


def _create_evaluation_prompt_for_single_criterion(criterion: Dict, response: str, prompt: str) -> str:
    return f"""
    Evaluate how well the following response meets the criterion '{criterion['name']}':
    Criterion description: {criterion['description']}

    Original prompt: {prompt}
    Generated response: {response}

    Provide a numerical score between 0-10 with 1 decimal place. 
    Consider both the response quality and relevance to the original prompt.
    Respond only with the numerical score.
    """


class PromptOptimizer:
    def __init__(self, api_key: str, criteria: List[Dict], max_iterations: int = 5,
                 score_threshold: float = 8.0, temperature: float = 0.5):
        self.api_key = api_key
        self.criteria = criteria
        self.max_iterations = max_iterations
        self.score_threshold = score_threshold
        self.temperature = temperature
        self.score_history = []

    def optimize_prompt(self, initial_prompt: str) -> Tuple[str, float]:
        current_prompt = initial_prompt
        best_score = 0.0
        best_prompt = current_prompt

        for iteration in range(self.max_iterations):
            response = ask_gemini(current_prompt, self.api_key)

            score = self._evaluate_response_score(response, current_prompt)
            self.score_history.append(score)

            if score >= self.score_threshold:
                break

            if score > best_score:
                best_score = score
                best_prompt = current_prompt

            current_prompt = self._generate_improved_prompt(current_prompt, score)

        return best_prompt, best_score

    def _evaluate_response_score(self, response: str, prompt: str) -> float:
        total_score = 0.0

        for criterion in self.criteria:
            eval_prompt = _create_evaluation_prompt_for_single_criterion(criterion, response, prompt)
            eval_response = ask_gemini(eval_prompt, self.api_key)
            score = _extract_score_from_response(eval_response)
            weighted_score = score * criterion.get('weight', 1.0)
            total_score += weighted_score

        sum_weights = sum(c.get('weight', 1.0) for c in self.criteria)
        return total_score / sum_weights

    def _generate_improved_prompt(self, current_prompt: str, current_score: float) -> str:
        improvement_prompt = f"""
        The current prompt: "{current_prompt}"
        Received an overall score of {current_score:.1f}/10 based on these criteria:
        {self._format_criteria_for_feedback()}

        Generate an improved prompt that would:
        1. Better address all the evaluation criteria
        2. Maintain clarity and focus
        3. Potentially yield higher-quality responses

        Provide only the new improved prompt between <PROMPT></PROMPT> tags.
        """

        improvement_response = ask_gemini(improvement_prompt, self.api_key)
        return _extract_prompt_from_response(improvement_response)

    def _format_criteria_for_feedback(self) -> str:
        return "\n".join([f"- {c['name']} (weight {c['weight']}): {c['description']}"
                          for c in self.criteria])
