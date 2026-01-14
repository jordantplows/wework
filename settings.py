from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Agent Settings
    DEFAULT_MODEL: str = "gpt-4"
    DEFAULT_PROVIDER: str = "openai"
    MAX_ITERATIONS: int = 10
    CODE_TIMEOUT: int = 30
    
    # Workspace Settings
    WORKSPACE_ROOT: str = "./workspaces"
    
    # Docker Settings
    DOCKER_IMAGE: str = "python:3.11-slim"
    DOCKER_MEM_LIMIT: str = "512m"
    DOCKER_CPU_QUOTA: int = 50000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()