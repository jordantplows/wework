from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from pathlib import Path
import uuid
from loguru import logger
from src.core.agent import Agent
from config.settings import settings

app = FastAPI(
    title="Agent Orchestration Platform",
    description="Headless autonomous agent platform with code execution",
    version="0.1.0"
)

# Store running agents
agents: Dict[str, Agent] = {}
agent_results: Dict[str, Dict[str, Any]] = {}

class AgentRequest(BaseModel):
    task: str
    provider: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    workspace_name: Optional[str] = None

class AgentResponse(BaseModel):
    agent_id: str
    workspace: str
    status: str

class AgentResult(BaseModel):
    agent_id: str
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    iterations: int
    history: Optional[List[Dict[str, Any]]] = None

async def run_agent_task(agent_id: str, agent: Agent, task: str):
    """Background task to run the agent"""
    try:
        logger.info(f"Starting background task for agent {agent_id}")
        result = await agent.run(task)
        agent_results[agent_id] = result
        logger.info(f"Agent {agent_id} completed")
    except Exception as e:
        logger.error(f"Agent {agent_id} failed: {e}")
        agent_results[agent_id] = {
            "success": False,
            "error": str(e),
            "iterations": agent.iteration_count
        }

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Agent Orchestration Platform",
        "version": "0.1.0",
        "status": "running",
        "active_agents": len(agents)
    }

@app.post("/agent/create", response_model=AgentResponse)
async def create_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """
    Create and start a new autonomous agent
    
    The agent will execute the given task using available tools and LLM.
    """
    try:
        # Generate unique agent ID
        agent_id = str(uuid.uuid4())
        
        # Create workspace
        workspace_name = request.workspace_name or agent_id
        workspace_path = Path(settings.WORKSPACE_ROOT) / workspace_name
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create agent
        agent = Agent(
            agent_id=agent_id,
            workspace_path=str(workspace_path),
            provider=request.provider,
            model=request.model,
            system_prompt=request.system_prompt
        )
        
        # Store agent
        agents[agent_id] = agent
        
        # Start agent in background
        background_tasks.add_task(run_agent_task, agent_id, agent, request.task)
        
        logger.info(f"Created agent {agent_id}")
        
        return AgentResponse(
            agent_id=agent_id,
            workspace=str(workspace_path),
            status="running"
        )
    
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get the current status of an agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_id]
    
    # Check if agent has completed
    if agent_id in agent_results:
        status = "completed" if agent_results[agent_id].get("success") else "failed"
    else:
        status = "running"
    
    return {
        "agent_id": agent_id,
        "status": status,
        **agent.get_state()
    }

@app.get("/agent/{agent_id}/result", response_model=AgentResult)
async def get_agent_result(agent_id: str, include_history: bool = False):
    """Get the result of a completed agent"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent_id not in agent_results:
        raise HTTPException(status_code=400, detail="Agent has not completed yet")
    
    result = agent_results[agent_id]
    
    return AgentResult(
        agent_id=agent_id,
        success=result.get("success", False),
        result=result.get("result"),
        error=result.get("error"),
        iterations=result.get("iterations", 0),
        history=result.get("history") if include_history else None
    )

@app.get("/agents")
async def list_agents():
    """List all agents"""
    agent_list = []
    
    for agent_id, agent in agents.items():
        status = "completed" if agent_id in agent_results else "running"
        agent_list.append({
            "agent_id": agent_id,
            "status": status,
            **agent.get_state()
        })
    
    return {
        "total": len(agent_list),
        "agents": agent_list
    }

@app.delete("/agent/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent and its results"""
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Remove from storage
    agents.pop(agent_id, None)
    agent_results.pop(agent_id, None)
    
    return {"message": f"Agent {agent_id} deleted"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_agents": len(agents)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info"
    )