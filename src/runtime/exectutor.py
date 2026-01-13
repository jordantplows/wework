# runtime/executor.py
import docker
import asyncio
from typing import Dict, Any

class CodeExecutor:
    def __init__(self, workspace_path: str):
        self.client = docker.from_env()
        self.workspace_path = workspace_path
    
    async def execute_python(
        self, 
        code: str, 
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Execute Python code in isolated container"""
        
        container = None
        try:
            container = self.client.containers.run(
                "python:3.11-slim",
                command=["python", "-c", code],
                detach=True,
                mem_limit="512m",
                volumes={
                    self.workspace_path: {
                        'bind': '/workspace',
                        'mode': 'rw'
                    }
                },
                working_dir="/workspace",
                network_disabled=False,  # Set True for more security
                remove=False
            )
            
            # Wait for completion
            result = container.wait(timeout=timeout)
            
            # Get output
            stdout = container.logs(stdout=True, stderr=False).decode()
            stderr = container.logs(stdout=False, stderr=True).decode()
            
            return {
                "success": result["StatusCode"] == 0,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": result["StatusCode"]
            }
            
        except docker.errors.ContainerError as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if container:
                container.remove(force=True)