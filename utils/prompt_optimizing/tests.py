import unittest
from unittest.mock import patch
from utils.prompt_optimizing.optimizer import _extract_prompt_from_response, _extract_score_from_response, \
    PromptOptimizer


class TestPromptOptimizer(unittest.TestCase):

    def test_extract_prompt_from_response(self):
        self.assertEqual(_extract_prompt_from_response("<PROMPT>Test prompt</PROMPT>"), "Test prompt")
        self.assertEqual(_extract_prompt_from_response("Some response"), "Some response")
        self.assertEqual(_extract_prompt_from_response("<PROMPT>  Trimmed </PROMPT>"), "Trimmed")

    def test_extract_score_from_response(self):
        self.assertEqual(_extract_score_from_response("<SCORE>8.5</SCORE>"), 8.5)
        self.assertEqual(_extract_score_from_response("reasoning <SCORE>7.2</SCORE> text"), 7.2)
        self.assertEqual(_extract_score_from_response("Invalid text"), 0.0)
        self.assertEqual(_extract_score_from_response("<SCORE>18.5</SCORE>"), 10.0)

    @patch("utils.llm_api.gemini_api.ask_gemini")
    def test_optimize_prompt(self, mock_ask_gemini):
        mock_ask_gemini.side_effect = [
            "<SCORE>6.0</SCORE><PROMPT>Improved Prompt 1</PROMPT>",
            "<SCORE>9.0</SCORE><PROMPT>Improved Prompt 2</PROMPT>",
        ]

        optimizer = PromptOptimizer(api_key="dummy_key",
                                    criteria=[{"name": "clarity", "description": "Should be clear"}], max_iterations=3,
                                    score_threshold=8.0)
        best_prompt, best_score = optimizer.optimize_prompt("Initial Prompt")

        self.assertEqual(best_prompt, "Improved Prompt 2")
        self.assertEqual(best_score, 9.0)

    @patch("prompt_optimizer.ask_gemini")
    def test_evaluate_and_improve(self, mock_ask_gemini):
        mock_ask_gemini.return_value = "<SCORE>7.5</SCORE><PROMPT>Better Prompt</PROMPT>"

        optimizer = PromptOptimizer(api_key="dummy_key",
                                    criteria=[{"name": "clarity", "description": "Should be clear"}])
        score, new_prompt = optimizer._evaluate_and_improve("Initial", "Generated Response")

        self.assertEqual(score, 7.5)
        self.assertEqual(new_prompt, "Better Prompt")


if __name__ == "__main__":
    unittest.main()
