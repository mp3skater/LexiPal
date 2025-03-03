from py.utils.prompt_optimizing import PromptOptimizer


def main():
    # Example configuration
    criteria = [
        {
            'name': 'Clarity',
            'description': 'Prompt should be unambiguous and easily understandable',
            'weight': 1.5
        },
        {
            'name': 'Relevance',
            'description': 'Response must address all aspects of the prompt',
            'weight': 1.2
        },
        {
            'name': 'Creativity',
            'description': 'Prompt should encourage original and innovative responses',
            'weight': 1.0
        }
    ]

    # Initialize optimizer with dummy API key
    optimizer = PromptOptimizer(
        api_key="your-api-key-here",
        criteria=criteria,
        max_iterations=5,
        score_threshold=8.5
    )

    # Run optimization
    initial_prompt = "Write a story about artificial intelligence"
    best_prompt, final_score = optimizer.optimize_prompt(initial_prompt)

    # Print full log
    print("\n" + "="*50 + " OPTIMIZATION LOG " + "="*50)
    for entry in optimizer.log_entries:
        print(f"\nITERATION {entry['iteration']} ({entry['status']})")
        print(f"\nCURRENT PROMPT:\n{entry['current_prompt']}")
        print(f"\nRESPONSE:\n{entry['response']}")
        print(f"\nSCORE: {entry['score']:.1f}")
        print(f"\nSUGGESTED IMPROVEMENT:\n{entry['new_prompt']}")
        print("\n" + "-"*100)

    # Print final results
    print("\n" + "="*50 + " FINAL RESULTS " + "="*50)
    print(f"\nBEST PROMPT (Score: {final_score:.1f}):\n{best_prompt}")


if __name__ == "__main__":
    main()
