# llm/gateway.py
from litellm import acompletion
from typing import List, Dict, Any

class LLMGateway:
    async def chat(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]] = None,
        **kwargs
    ):
        """Unified interface for all LLM providers"""
        
        model_string = f"{provider}/{model}"
        
        response = await acompletion(
            model=model_string,
            messages=messages,
            tools=tools,
            **kwargs
        )
        
        return response