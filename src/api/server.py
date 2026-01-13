# api/server.py
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    task: str
    llm_provider: str
    model: str
    tools: List[str]
    files: List[str] = []

@app.post("/agent/create")
async def create_agent(request: AgentRequest):
    """Create and start a new agent"""
    agent_id = generate_id()
    
    # Initialize agent with tools
    agent = Agent(
        agent_id=agent_id,
        llm_provider=request.llm_provider,
        tools=load_tools(request.tools),
        system_prompt=DEFAULT_SYSTEM_PROMPT
    )
    
    # Queue the task
    task_id = queue_agent_task(agent, request.task)
    
    return {
        "agent_id": agent_id,
        "task_id": task_id,
        "status": "queued"
    }

@app.websocket("/agent/{agent_id}/stream")
async def agent_stream(websocket: WebSocket, agent_id: str):
    """Stream agent progress in real-time"""
    await websocket.accept()
    
    # Subscribe to agent events
    async for event in agent_event_stream(agent_id):
        await websocket.send_json(event)