import re
from typing import List, Dict, Tuple

from utils.llm_api.gemini_api.gemini_api import ask_gemini
from utils.llm_api.questions_handler.question_handler import ask_questions


class PromptOptimizer:
    def __init__(
            self,
            initial_questions: List[str],
            perfect_examples: List[str],  # Parallel list to initial_questions
            rules: Dict[str, List[str]],  # {"must": [], "must_not": []}
            score_threshold: float = 0.8,
            max_iterations: int = 5,
    ):
        self.questions = initial_questions
        self.perfect_examples = perfect_examples
        self.rules = rules
        self.score_threshold = score_threshold
        self.max_iterations = max_iterations
        self.logs = []

    def optimize(self, api_key: str) -> Dict:
        """
        Returns: {
            "success": bool,
            "optimized_prompt": str,
            "optimized_questions": List[str],
            "best_score": float,
            "logs": List[Dict]
        }
        """
        current_prompt = "\n".join(self.questions)
        iteration = 0

        while iteration < self.max_iterations:
            # Get answers for all questions
            answers, raw_response = ask_questions(self.questions, api_key)

            # Score answers
            scores, violations, score_feedback = self.score_answers(answers, api_key)

            # Check for absolute failures
            if any(violations):
                self.log_iteration(iteration, current_prompt, answers, scores,
                                   "ABORT: Must-not rule violated", violations)
                return self.finalize_result(False, current_prompt, scores)

            # Check if all questions meet threshold
            if scores and (len(scores) == len(self.questions)) and all(s >= self.score_threshold for s in scores):
                self.log_iteration(iteration, current_prompt, answers, scores,
                                   "SUCCESS: All thresholds met")
                return self.finalize_result(True, current_prompt, scores)

            # Refine prompts using self-reflection
            refinement = self.refine_prompt(current_prompt, answers, scores,
                                            score_feedback, api_key)
            current_prompt = refinement
            self.questions = self.parse_refined_prompt(refinement)

            iteration += 1

        return self.finalize_result(False, current_prompt, scores)

    def score_answers(self, answers: List[str], api_key: str) -> Tuple[List[float], List[bool], str]:
        """
        Returns: (scores, violations, feedback)
        """
        scoring_prompt = f"""
        Evaluate these answers against rules and perfect examples. Respond with:
        [Score X/Y] per answer (0.0-1.0), [Violation? True/False], [Feedback]

        Rules:
        Must: {self.rules['must']}
        Must Not: {self.rules['must_not']}

        Perfect Examples: {self.perfect_examples}

        Answers to score: {answers}
        """

        try:
            score_response = ask_gemini(scoring_prompt, api_key)
            if "ERROR" in score_response:
                raise ValueError("API returned error")
            return self.parse_score_response(score_response)
        except Exception as e:
            print(f"Scoring failed: {str(e)}")
            return [0.0] * len(self.questions), [False] * len(self.questions), "Scoring error"

    def parse_score_response(self, response: str) -> Tuple[List[float], List[bool], str]:
        print(f"\n[DEBUG] Raw scoring response:\n{response}")

        # Handle both "Score 0.8" and "Score 4/5" formats
        pattern = r'\[Score\s+([\d.]+)(?:/|\s+out of\s+)([\d.]+)?\]\s*\[Violation\?\s*(True|False)\]'

        scores = []
        violations = []
        for match in re.finditer(pattern, response):
            try:
                numerator = float(match.group(1))
                denominator = float(match.group(2)) if match.group(2) else 1.0
                score = numerator / denominator
            except:
                score = 0.0
            scores.append(min(max(score, 0.0), 1.0))
            violations.append(match.group(3).lower() == "true")

        # Fallback if no matches
        if not scores:
            print("[WARNING] Failed to parse scores, using defaults")
            scores = [0.0] * len(self.questions)
            violations = [False] * len(self.questions)

        return scores, violations, response

    def refine_prompt(self, current_prompt: str, answers: List[str],
                      scores: List[float], feedback: str, api_key: str) -> str:
        refinement_prompt = f"""
        Improve this prompt based on scores and feedback. Follow MUST/MUST NOT rules.

        Current prompt: {current_prompt}
        Answers: {answers}
        Scores: {scores}
        Feedback: {feedback}

        Rules: {self.rules}
        Perfect examples: {self.perfect_examples}

        Return ONLY the improved prompt.
        """
        return ask_gemini(refinement_prompt, api_key)

    def parse_refined_prompt(self, refinement: str) -> List[str]:
        questions = []
        for line in refinement.strip().split("\n"):
            # Handle "1. Question" or "Question" formats
            if ". " in line:
                try:
                    q = line.split(". ", 1)[1].strip()
                    questions.append(q)
                except IndexError:
                    questions.append(line.strip())
            else:
                questions.append(line.strip())
        return questions

    def log_iteration(self, iteration: int, prompt: str, answers: List[str],
                      scores: List[float], status: str, violations: List[bool] = None):
        self.logs.append({
            "iteration": iteration,
            "prompt": prompt,
            "answers": answers,
            "scores": scores,
            "violations": violations,
            "status": status
        })

    def finalize_result(self, success: bool, final_prompt: str,
                        final_scores: List[float]) -> Dict:
        return {
            "success": success,
            "optimized_prompt": final_prompt,
            "optimized_questions": self.questions,
            "best_score": min(final_scores) if final_scores else 0.0,
            "logs": self.logs
        }
