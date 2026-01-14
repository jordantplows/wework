"""
Example usage of the Agent Orchestration Platform

This script demonstrates how to use the agent platform programmatically.
"""

import asyncio
from pathlib import Path
from src.core.agent import Agent
from loguru import logger
import sys

# Configure logging
logger.remove()
logger.add(sys.stdout, level="INFO")

async def example_1_simple_task():
    """Example: Simple file creation task"""
    print("\n=== Example 1: Simple File Creation ===\n")
    
    agent = Agent(
        agent_id="example-1",
        workspace_path="./workspaces/example-1"
    )
    
    task = """
    Create a Python script called 'hello.py' that prints "Hello from the agent!"
    Then execute the script to verify it works.
    """
    
    result = await agent.run(task)
    
    print(f"Success: {result['success']}")
    print(f"Iterations: {result['iterations']}")
    print(f"Result: {result['result']}")

async def example_2_data_processing():
    """Example: Data processing task"""
    print("\n=== Example 2: Data Processing ===\n")
    
    agent = Agent(
        agent_id="example-2",
        workspace_path="./workspaces/example-2"
    )
    
    task = """
    1. Create a CSV file called 'data.csv' with sample sales data (product, quantity, price)
    2. Write a Python script to read the CSV and calculate total revenue
    3. Execute the script and save the results to 'report.txt'
    """
    
    result = await agent.run(task)
    
    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")

async def example_3_code_analysis():
    """Example: Code analysis task"""
    print("\n=== Example 3: Code Analysis ===\n")
    
    # First create a sample file
    workspace = Path("./workspaces/example-3")
    workspace.mkdir(parents=True, exist_ok=True)
    
    sample_code = '''
def calculate_factorial(n):
    if n == 0:
        return 1
    return n * calculate_factorial(n-1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(calculate_factorial(5))
print(fibonacci(10))
'''
    
    (workspace / "sample.py").write_text(sample_code)
    
    agent = Agent(
        agent_id="example-3",
        workspace_path=str(workspace)
    )
    
    task = """
    1. Read the file 'sample.py'
    2. Analyze the code for potential performance issues
    3. Create an optimized version called 'sample_optimized.py'
    4. Test both versions and compare their performance
    """
    
    result = await agent.run(task)
    
    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")

async def example_4_web_scraping():
    """Example: Install packages and use them"""
    print("\n=== Example 4: Package Installation ===\n")
    
    agent = Agent(
        agent_id="example-4",
        workspace_path="./workspaces/example-4"
    )
    
    task = """
    1. Install the 'requests' package using pip
    2. Create a Python script that makes a request to httpbin.org/json
    3. Save the response to 'response.json'
    4. Execute the script
    """
    
    result = await agent.run(task)
    
    print(f"Success: {result['success']}")
    print(f"Result: {result['result']}")

async def main():
    """Run all examples"""
    
    print("Agent Orchestration Platform - Examples")
    print("=" * 50)
    
    # Run examples
    await example_1_simple_task()
    await example_2_data_processing()
    await example_3_code_analysis()
    await example_4_web_scraping()
    
    print("\n" + "=" * 50)
    print("All examples completed!")

if __name__ == "__main__":
    asyncio.run(main())