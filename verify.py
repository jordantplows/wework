#!/usr/bin/env python3
"""
System Verification Test

Run this script to verify your installation is working correctly.
"""

import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def check_python():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 11:
        print("✅ Python version OK")
        return True
    else:
        print("❌ Python 3.11+ required")
        return False

def check_docker():
    """Check Docker installation"""
    print_header("Checking Docker")
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout.strip())
        print("✅ Docker is installed")
        
        # Check if Docker is running
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Docker is running")
        return True
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker.")
        return False
    except subprocess.CalledProcessError:
        print("❌ Docker is installed but not running. Please start Docker.")
        return False

def check_dependencies():
    """Check Python dependencies"""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "litellm",
        "docker",
        "aiofiles",
        "loguru"
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} not found")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_env_file():
    """Check for .env file"""
    print_header("Checking Configuration")
    
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if env_path.exists():
        print("✅ .env file exists")
        
        # Check if it has API keys
        content = env_path.read_text()
        if "your_" in content or "sk-" not in content:
            print("⚠️  Warning: .env file may not have valid API keys")
            print("   Edit .env and add your API key")
        else:
            print("✅ .env appears to be configured")
        return True
    else:
        print("❌ .env file not found")
        if env_example.exists():
            print("   Run: cp .env.example .env")
            print("   Then edit .env and add your API key")
        return False

def check_structure():
    """Check project structure"""
    print_header("Checking Project Structure")
    
    required_dirs = [
        "src/core",
        "src/llm",
        "src/runtime",
        "src/tools",
        "src/api",
        "config",
        "examples"
    ]
    
    required_files = [
        "requirements.txt",
        "README.md",
        "run.py"
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ not found")
            all_good = False
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} not found")
            all_good = False
    
    return all_good

def run_simple_test():
    """Run a simple import test"""
    print_header("Testing Imports")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        
        from src.core.agent import Agent
        print("✅ Can import Agent")
        
        from src.llm.gateway import LLMGateway
        print("✅ Can import LLMGateway")
        
        from src.runtime.executor import CodeExecutor
        print("✅ Can import CodeExecutor")
        
        from src.tools.file_tools import FileTool
        print("✅ Can import FileTool")
        
        from config.settings import settings
        print("✅ Can import settings")
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║   Agent Orchestration Platform - System Check        ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # Run all checks
    results.append(("Python Version", check_python()))
    results.append(("Docker", check_docker()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("Configuration", check_env_file()))
    results.append(("Project Structure", check_structure()))
    results.append(("Import Test", run_simple_test()))
    
    # Summary
    print_header("Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your system is ready.")
        print("\nNext steps:")
        print("1. Make sure you've added your API key to .env")
        print("2. Try: python run.py example")
        print("3. Or start the server: python run.py server")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())