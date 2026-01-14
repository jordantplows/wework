"""
Example of using the Agent Platform via HTTP API

This demonstrates how external applications can integrate with the platform.
"""

import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"

def create_agent(task, provider="openai", model="gpt-4"):
    """Create a new agent"""
    response = requests.post(
        f"{BASE_URL}/agent/create",
        json={
            "task": task,
            "provider": provider,
            "model": model
        }
    )
    response.raise_for_status()
    return response.json()

def get_agent_status(agent_id):
    """Get agent status"""
    response = requests.get(f"{BASE_URL}/agent/{agent_id}/status")
    response.raise_for_status()
    return response.json()

def get_agent_result(agent_id, include_history=False):
    """Get agent result"""
    response = requests.get(
        f"{BASE_URL}/agent/{agent_id}/result",
        params={"include_history": include_history}
    )
    response.raise_for_status()
    return response.json()

def wait_for_agent(agent_id, max_wait=300, poll_interval=2):
    """Wait for agent to complete"""
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status = get_agent_status(agent_id)
        
        if status["status"] in ["completed", "failed"]:
            return status
        
        print(f"Agent {agent_id}: {status['status']} (iteration {status['iterations']})")
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Agent {agent_id} did not complete within {max_wait} seconds")

def example_1():
    """Simple file creation task"""
    print("\n=== Example 1: Create and Execute Python Script ===\n")
    
    task = """
    Create a Python script that:
    1. Generates 100 random numbers
    2. Calculates mean, median, and standard deviation
    3. Saves the results to a file called 'stats.txt'
    Then execute the script.
    """
    
    # Create agent
    agent = create_agent(task)
    agent_id = agent["agent_id"]
    print(f"Created agent: {agent_id}")
    print(f"Workspace: {agent['workspace']}")
    
    # Wait for completion
    status = wait_for_agent(agent_id)
    print(f"\nAgent status: {status['status']}")
    
    # Get result
    result = get_agent_result(agent_id)
    print(f"\nSuccess: {result['success']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Result:\n{result['result']}")

def example_2():
    """Data processing task"""
    print("\n=== Example 2: CSV Data Analysis ===\n")
    
    task = """
    Create a sales dataset and analyze it:
    1. Create a CSV file with 50 rows of sales data (date, product, quantity, price)
    2. Write a Python script to analyze this data
    3. Calculate total revenue, average sale, and top 5 products
    4. Create a summary report in 'analysis.txt'
    """
    
    agent = create_agent(task)
    agent_id = agent["agent_id"]
    print(f"Created agent: {agent_id}")
    
    status = wait_for_agent(agent_id)
    print(f"Agent status: {status['status']}")
    
    result = get_agent_result(agent_id)
    print(f"\nResult:\n{result['result']}")

def example_3():
    """Multi-step automation"""
    print("\n=== Example 3: Multi-step Automation ===\n")
    
    task = """
    Build a simple task management system:
    1. Create a JSON file to store tasks
    2. Write a Python script with functions to:
       - Add a task
       - List all tasks
       - Mark a task as complete
    3. Add 3 sample tasks
    4. Mark one as complete
    5. List all tasks to verify
    """
    
    agent = create_agent(task, model="gpt-4")
    agent_id = agent["agent_id"]
    print(f"Created agent: {agent_id}")
    
    status = wait_for_agent(agent_id)
    result = get_agent_result(agent_id, include_history=True)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Total iterations: {result['iterations']}")
    print(f"\nFinal result:\n{result['result']}")
    
    if result['history']:
        print(f"\nTotal conversation turns: {len(result['history'])}")

def list_all_agents():
    """List all agents"""
    print("\n=== All Agents ===\n")
    
    response = requests.get(f"{BASE_URL}/agents")
    data = response.json()
    
    print(f"Total agents: {data['total']}\n")
    
    for agent in data['agents']:
        print(f"Agent ID: {agent['agent_id']}")
        print(f"  Status: {agent['status']}")
        print(f"  Iterations: {agent['iterations']}")
        print(f"  Workspace: {agent['workspace']}")
        print()

def main():
    """Run examples"""
    print("Agent Orchestration Platform - API Examples")
    print("=" * 60)
    
    # Check API health
    try:
        response = requests.get(f"{BASE_URL}/health")
        health = response.json()
        print(f"\nAPI Status: {health['status']}")
        print(f"Active agents: {health['active_agents']}\n")
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API server.")
        print("Please start the server with: python -m src.api.server")
        return
    
    # Run examples
    try:
        example_1()
        example_2()
        example_3()
        
        # List all agents
        list_all_agents()
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()