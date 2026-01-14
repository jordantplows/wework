import aiofiles
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
import json

class FileTool:
    """Base class for file manipulation tools"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path).absolute()
        self.workspace_path.mkdir(parents=True, exist_ok=True)
    
    def _validate_path(self, filepath: str) -> Path:
        """Ensure file path is within workspace"""
        full_path = (self.workspace_path / filepath).resolve()
        
        # Security: prevent path traversal
        if not str(full_path).startswith(str(self.workspace_path)):
            raise ValueError(f"Access denied: {filepath} is outside workspace")
        
        return full_path
    
    async def read_file(self, filepath: str) -> str:
        """Read file contents"""
        try:
            path = self._validate_path(filepath)
            
            if not path.exists():
                return f"Error: File {filepath} does not exist"
            
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            logger.info(f"Read file: {filepath} ({len(content)} chars)")
            return content
        
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return f"Error reading file: {str(e)}"
    
    async def write_file(self, filepath: str, content: str) -> str:
        """Write content to file"""
        try:
            path = self._validate_path(filepath)
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            logger.info(f"Wrote file: {filepath} ({len(content)} chars)")
            return f"Successfully wrote {len(content)} characters to {filepath}"
        
        except Exception as e:
            logger.error(f"Error writing {filepath}: {e}")
            return f"Error writing file: {str(e)}"
    
    async def list_files(self, directory: str = ".") -> str:
        """List files in directory"""
        try:
            path = self._validate_path(directory)
            
            if not path.exists():
                return f"Error: Directory {directory} does not exist"
            
            if not path.is_dir():
                return f"Error: {directory} is not a directory"
            
            files = []
            for item in path.iterdir():
                file_type = "dir" if item.is_dir() else "file"
                size = item.stat().st_size if item.is_file() else 0
                files.append({
                    "name": item.name,
                    "type": file_type,
                    "size": size
                })
            
            logger.info(f"Listed {len(files)} items in {directory}")
            return json.dumps(files, indent=2)
        
        except Exception as e:
            logger.error(f"Error listing {directory}: {e}")
            return f"Error listing directory: {str(e)}"
    
    async def delete_file(self, filepath: str) -> str:
        """Delete a file"""
        try:
            path = self._validate_path(filepath)
            
            if not path.exists():
                return f"Error: File {filepath} does not exist"
            
            path.unlink()
            logger.info(f"Deleted file: {filepath}")
            return f"Successfully deleted {filepath}"
        
        except Exception as e:
            logger.error(f"Error deleting {filepath}: {e}")
            return f"Error deleting file: {str(e)}"
    
    async def create_directory(self, directory: str) -> str:
        """Create a directory"""
        try:
            path = self._validate_path(directory)
            path.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Created directory: {directory}")
            return f"Successfully created directory {directory}"
        
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
            return f"Error creating directory: {str(e)}"

def get_file_tools_definition() -> List[Dict[str, Any]]:
    """Get tool definitions for LLM"""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_file",
                "description": "Read the contents of a file from the workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file relative to workspace root"
                        }
                    },
                    "required": ["filepath"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": "Write content to a file in the workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file relative to workspace root"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["filepath", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_files",
                "description": "List all files and directories in a directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path relative to workspace root (default: '.')",
                            "default": "."
                        }
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_directory",
                "description": "Create a new directory in the workspace",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directory path relative to workspace root"
                        }
                    },
                    "required": ["directory"]
                }
            }
        }
    ]