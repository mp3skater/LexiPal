import os

from utils.prompt_optimizer.auto_prompt_optimizer import PromptOptimizer

API_KEY = os.getenv("GEMINI_API")

if __name__ == '__main__':
    optimizer = PromptOptimizer(
        initial_questions=[
            "What is AI?",
            "List 3 AI applications"
        ],
        perfect_examples=[
            "Artificial intelligence is the simulation of human intelligence processes by machines.",
            "1. Medical diagnosis 2. Speech recognition 3. Fraud detection"
        ],
        rules={
            "must": ["Answers under 50 words"],
            "must_not": ["Technical jargon", "Markdown formatting"]
        },
        score_threshold=0.7,
        max_iterations=3
    )

    # Run optimization
    result = optimizer.optimize(api_key=API_KEY)

    # Print everything
    print("=== Optimization Result ===")
    print(f"Success: {result['success']}")
    print(f"Best Score: {result['best_score']}")
    print("\n=== Optimized Prompt ===")
    print(result["optimized_prompt"])
    print("\n=== Optimized Questions ===")
    for i, q in enumerate(result["optimized_questions"], 1):
        print(f"{i}. {q}")
    print("\n=== Full Logs ===")
    for log in result["logs"]:
        print(f"\nIteration {log['iteration']}: {log['status']}")
        print(f"Prompt: {log['prompt']}")
        print("Answers:")
        for i, (ans, score) in enumerate(zip(log["answers"], log["scores"]), 1):
            print(f"  {i}. [Score: {score:.2f}] {ans}")
        if log["violations"]:
            print(f"Violations: {log['violations']}")
