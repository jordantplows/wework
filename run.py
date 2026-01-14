#!/usr/bin/env python3
"""
Main entry point for the Agent Orchestration Platform

Usage:
    python run.py server              # Start the API server
    python run.py example             # Run basic examples
    python run.py api-example         # Run API client examples
"""

import sys
import asyncio
import uvicorn
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def run_server():
    """Start the FastAPI server"""
    from config.settings import settings
    
    print("🚀 Starting Agent Orchestration Platform API Server")
    print(f"📍 Server: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"🔧 Provider: {settings.DEFAULT_PROVIDER}/{settings.DEFAULT_MODEL}")
    print()
    
    uvicorn.run(
        "src.api.server:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level="info"
    )

def run_examples():
    """Run basic examples"""
    print("🤖 Running Agent Examples")
    print()
    
    import examples.basic_usage as basic
    asyncio.run(basic.main())

def run_api_examples():
    """Run API client examples"""
    print("🌐 Running API Client Examples")
    print()
    
    import examples.api_client as api_client
    api_client.main()

def show_help():
    """Show help message"""
    print("""
Agent Orchestration Platform
=============================

Usage:
    python run.py <command>

Commands:
    server          Start the API server
    example         Run basic Python examples
    api-example     Run API client examples (requires server running)
    help            Show this help message

Setup:
    1. Copy .env.example to .env and add your API keys
    2. Ensure Docker is running
    3. Install dependencies: pip install -r requirements.txt

Quick Start:
    # Start server
    python run.py server

    # In another terminal, run examples
    python run.py api-example

More Info:
    See README.md for detailed documentation
    """)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "server":
        run_server()
    elif command == "example":
        run_examples()
    elif command == "api-example":
        run_api_examples()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()