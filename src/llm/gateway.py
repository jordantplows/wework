from typing import List, Dict, Any, Optional
from litellm import acompletion
from loguru import logger

class LLMGateway:
    """Unified interface for multiple LLM providers"""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-4"):
        self.provider = provider
        self.model = model
        self.model_string = f"{provider}/{model}"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the LLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict with content and optional tool_calls
        """
        try:
            logger.info(f"Calling {self.model_string} with {len(messages)} messages")
            
            response = await acompletion(
                model=self.model_string,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            # Extract the response
            message = response.choices[0].message
            
            result = {
                "content": message.content or "",
                "tool_calls": []
            }
            
            # Check for tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                    for tc in message.tool_calls
                ]
            
            logger.info(f"Response: {len(result['content'])} chars, {len(result['tool_calls'])} tool calls")
            return result
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def format_tool_definition(self, name: str, description: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Format a tool definition for the LLM"""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }