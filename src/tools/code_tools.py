from typing import List, Dict, Any
from src.runtime.executor import CodeExecutor
from loguru import logger
import json

class CodeTools:
    """Tools for executing code"""
    
    def __init__(self, executor: CodeExecutor):
        self.executor = executor
    
    async def execute_python(self, code: str) -> str:
        """Execute Python code"""
        logger.info("Executing Python code via tool")
        result = await self.executor.execute_python(code)
        
        # Format response for LLM
        if result["success"]:
            return f"Code executed successfully.\n\nOutput:\n{result['stdout']}"
        else:
            error_msg = result.get('stderr', result.get('error', 'Unknown error'))
            return f"Code execution failed.\n\nError:\n{error_msg}"
    
    async def execute_bash(self, command: str) -> str:
        """Execute bash command"""
        logger.info(f"Executing bash command via tool: {command}")
        result = await self.executor.execute_bash(command)
        
        if result["success"]:
            return f"Command executed successfully.\n\nOutput:\n{result['stdout']}"
        else:
            error_msg = result.get('stderr', result.get('error', 'Unknown error'))
            return f"Command execution failed.\n\nError:\n{error_msg}"

def get_code_tools_definition() -> List[Dict[str, Any]]:
    """Get tool definitions for LLM"""
    return [
        {
            "type": "function",
            "function": {
                "name": "execute_python",
                "description": "Execute Python code in an isolated environment. The code has access to the workspace directory mounted at /workspace. Use this to run Python scripts, process data, or perform computations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Python code to execute"
                        }
                    },
                    "required": ["code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_bash",
                "description": "Execute a bash command in an isolated environment. The workspace directory is mounted at /workspace. Use this for file operations, running shell commands, or installing packages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    ]