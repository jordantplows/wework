# core/agent.py
from typing import List, Dict, Any
from pydantic import BaseModel

class Tool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    
    async def execute(self, **kwargs) -> Any:
        raise NotImplementedError

class Agent:
    def __init__(
        self,
        agent_id: str,
        llm_provider: str,
        tools: List[Tool],
        system_prompt: str
    ):
        self.agent_id = agent_id
        self.llm_provider = llm_provider
        self.tools = {t.name: t for t in tools}
        self.system_prompt = system_prompt
        self.conversation_history = []
        self.state = {}
    
    async def run(self, task: str):
        """Main agent loop"""
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        
        while not self.is_complete():
            # Get LLM response
            response = await self.llm_call()
            
            # Check for tool calls
            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    result = await self.execute_tool(tool_call)
                    self.conversation_history.append({
                        "role": "tool",
                        "content": result
                    })
            else:
                # Final response
                return response["content"]
    
    async def execute_tool(self, tool_call):
        tool = self.tools.get(tool_call["name"])
        if not tool:
            return f"Error: Tool {tool_call['name']} not found"
        
        return await tool.execute(**tool_call["arguments"])