import os

from utils.prompt_optimizing.optimizer import PromptOptimizer

API_KEY = os.getenv("GEMINI_API")

if __name__ == "__main__":
    criteria = [
        {
            "name": "Clarity",
            "description": "Response should be clear and easy to understand",
            "weight": 1.2
        },
        {
            "name": "Relevance",
            "description": "Response should stay focused on the query topic",
            "weight": 1.0
        },
        {
            "name": "Depth",
            "description": "Response should provide comprehensive insights",
            "weight": 0.8
        }
    ]

    optimizer = PromptOptimizer(
        api_key=API_KEY,
        criteria=criteria,
        max_iterations=5,
        score_threshold=8.5
    )

    initial_prompt = "Explain machine learning in simple terms"
    optimized_prompt, final_score = optimizer.optimize_prompt(initial_prompt)

    print(f"Optimized Prompt ({final_score:.1f}/10):")
    print(optimized_prompt)
