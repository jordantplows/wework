from typing import List, Dict, Any, Optional
from loguru import logger
from src.llm.gateway import LLMGateway
from src.runtime.executor import CodeExecutor
from src.tools.file_tools import FileTool, get_file_tools_definition
from src.tools.code_tools import CodeTools, get_code_tools_definition
from config.settings import settings
import json

class Agent:
    """Autonomous agent that can execute tasks using LLM and tools"""
    
    def __init__(
        self,
        agent_id: str,
        workspace_path: str,
        provider: str = None,
        model: str = None,
        system_prompt: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.workspace_path = workspace_path
        
        # Initialize LLM
        provider = provider or settings.DEFAULT_PROVIDER
        model = model or settings.DEFAULT_MODEL
        self.llm = LLMGateway(provider=provider, model=model)
        
        # Initialize tools
        self.executor = CodeExecutor(workspace_path)
        self.file_tool = FileTool(workspace_path)
        self.code_tool = CodeTools(self.executor)
        
        # Conversation state
        self.conversation_history = []
        self.iteration_count = 0
        self.max_iterations = settings.MAX_ITERATIONS
        
        # System prompt
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        logger.info(f"Agent {agent_id} initialized with {provider}/{model}")
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for the agent"""
        return """You are an autonomous AI agent with access to a workspace and code execution capabilities.

You can:
- Read and write files in your workspace
- Execute Python code and bash commands
- Create and organize directories
- Process data and perform computations

When given a task:
1. Break it down into clear steps
2. Use your tools to accomplish each step
3. Verify your work
4. Report results clearly

Always explain your reasoning and what you're doing. If you encounter errors, analyze them and try alternative approaches.

You have access to these tools:
- read_file: Read file contents
- write_file: Write content to a file
- list_files: List files in a directory
- create_directory: Create a new directory
- execute_python: Execute Python code
- execute_bash: Execute bash commands

Work systematically and thoroughly to complete your tasks."""
    
    def _get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tool definitions"""
        return get_file_tools_definition() + get_code_tools_definition()
    
    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        try:
            # Parse arguments if they're a string
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            logger.info(f"Executing tool: {tool_name}")
            logger.debug(f"Arguments: {arguments}")
            
            # File tools
            if tool_name == "read_file":
                return await self.file_tool.read_file(arguments["filepath"])
            elif tool_name == "write_file":
                return await self.file_tool.write_file(
                    arguments["filepath"],
                    arguments["content"]
                )
            elif tool_name == "list_files":
                directory = arguments.get("directory", ".")
                return await self.file_tool.list_files(directory)
            elif tool_name == "create_directory":
                return await self.file_tool.create_directory(arguments["directory"])
            
            # Code tools
            elif tool_name == "execute_python":
                return await self.code_tool.execute_python(arguments["code"])
            elif tool_name == "execute_bash":
                return await self.code_tool.execute_bash(arguments["command"])
            
            else:
                return f"Error: Unknown tool '{tool_name}'"
        
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing {tool_name}: {str(e)}"
    
    async def run(self, task: str) -> Dict[str, Any]:
        """
        Run the agent on a task
        
        Args:
            task: The task description
            
        Returns:
            Dict with success status, result, and conversation history
        """
        logger.info(f"Agent {self.agent_id} starting task: {task[:100]}...")
        
        # Add user task to conversation
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        
        self.iteration_count = 0
        
        try:
            while self.iteration_count < self.max_iterations:
                self.iteration_count += 1
                logger.info(f"Iteration {self.iteration_count}/{self.max_iterations}")
                
                # Get LLM response
                response = await self.llm.chat(
                    messages=self.conversation_history,
                    tools=self._get_all_tools()
                )
                
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response["content"]
                })
                
                # Check if there are tool calls
                if response["tool_calls"]:
                    logger.info(f"Processing {len(response['tool_calls'])} tool calls")
                    
                    # Execute each tool call
                    for tool_call in response["tool_calls"]:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["arguments"]
                        
                        # Execute the tool
                        result = await self._execute_tool(tool_name, tool_args)
                        
                        # Add tool result to conversation
                        self.conversation_history.append({
                            "role": "user",
                            "content": f"Tool '{tool_name}' result:\n{result}"
                        })
                    
                    # Continue the loop to get next response
                    continue
                
                # No tool calls - agent is done
                logger.info("Agent completed task (no more tool calls)")
                return {
                    "success": True,
                    "result": response["content"],
                    "iterations": self.iteration_count,
                    "history": self.conversation_history
                }
            
            # Max iterations reached
            logger.warning(f"Agent reached max iterations ({self.max_iterations})")
            return {
                "success": False,
                "result": "Maximum iterations reached without completion",
                "iterations": self.iteration_count,
                "history": self.conversation_history
            }
        
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "iterations": self.iteration_count,
                "history": self.conversation_history
            }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return {
            "agent_id": self.agent_id,
            "workspace": self.workspace_path,
            "iterations": self.iteration_count,
            "max_iterations": self.max_iterations,
            "conversation_length": len(self.conversation_history)
        }