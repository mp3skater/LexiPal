##############################
# base_llm_client.py (Abstract Interface)
##############################
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLMClient(ABC):
    @abstractmethod
    def query(self, system_prompt: str, user_inputs: List[str]) -> List[Dict]:
        """
        Implement this with your actual LLM API module
        Returns list of responses in format:
        [{
            'id': 'request1',
            'response': '...',
            'metadata': {...}
        }]
        """
        pass
