import os

from utils.prompt_optimizing.optimizer import PromptOptimizer

API_KEY = os.getenv("GEMINI_API")

criteria = [
    {'name': 'Clarity', 'description': 'Prompt should be unambiguous', 'weight': 1.5},
    {'name': 'Relevance', 'description': 'Response must address all prompt aspects', 'weight': 1.0}
]

optimizer = PromptOptimizer(api_key=API_KEY, criteria=criteria)
improved_prompt, final_score = optimizer.optimize_prompt("Explain ai to a 12 year old")
