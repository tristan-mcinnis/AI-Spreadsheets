#!/usr/bin/env python3
"""
Simple launcher for HF Sheets
Run with: python run.py
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return the process"""
    try:
        return subprocess.Popen(cmd, cwd=cwd, shell=shell)
    except Exception as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e}")
        return None

def check_requirements():
    """Check if Python and Node are available"""
    print("🔍 Checking requirements...")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"✅ Python: {result.stdout.strip()}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except:
        print("❌ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except:
        print("⚠️  npm not found in PATH, but Node.js is available")
        print("   You may need to install frontend dependencies manually")
    
    return True

def setup_backend():
    """Set up Python backend"""
    backend_dir = Path("backend")
    
    print("🐍 Setting up Python backend...")
    
    # Check if conda is available
    conda_available = False
    try:
        subprocess.run(["conda", "--version"], capture_output=True, check=True)
        conda_available = True
        print("✅ Conda detected - using conda environment")
    except:
        print("📦 Using pip/venv environment")
    
    if conda_available:
        # Use conda environment
        env_name = "hf-sheets"
        try:
            # Check if environment exists
            result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True)
            if env_name not in result.stdout:
                print(f"Creating conda environment: {env_name}")
                subprocess.run(["conda", "create", "-n", env_name, "python=3.11", "-y"])
            
            print("Installing Python dependencies with conda environment...")
            if os.name == 'nt':  # Windows
                subprocess.run(f"conda activate {env_name} && pip install -r requirements.txt", shell=True, cwd=backend_dir)
                python_path = f"conda run -n {env_name} python"
            else:
                subprocess.run(f"conda activate {env_name} && pip install -r requirements.txt", shell=True, cwd=backend_dir)
                python_path = f"conda run -n {env_name} python"
            
            return python_path
            
        except Exception as e:
            print(f"Conda setup failed: {e}, falling back to venv")
            conda_available = False
    
    if not conda_available:
        # Fallback to venv
        venv_dir = backend_dir / "venv"
        
        # Create virtual environment if it doesn't exist
        if not venv_dir.exists():
            print("Creating Python virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
        
        # Install dependencies
        if os.name == 'nt':  # Windows
            pip_path = venv_dir / "Scripts" / "pip"
            python_path = venv_dir / "Scripts" / "python"
        else:  # Unix/Mac
            pip_path = venv_dir / "bin" / "pip"
            python_path = venv_dir / "bin" / "python"
        
        print("Installing Python dependencies...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], cwd=backend_dir)
        
        return str(python_path)

def setup_frontend():
    """Set up React frontend"""
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    
    print("⚛️ Setting up React frontend...")
    
    if not node_modules.exists():
        print("Installing Node.js dependencies...")
        try:
            subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️  Could not run npm install automatically.")
            print("Please run this manually in another terminal:")
            print(f"cd {frontend_dir.absolute()}")
            print("npm install")
            input("Press Enter after you've installed the dependencies...")

def check_env_file():
    """Check if .env file exists"""
    env_file = Path("backend") / ".env"
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("Please create backend/.env with your OpenAI API key:")
        print("OPENAI_API_KEY=sk-your-key-here")
        print("DEBUG=True")
        print("CORS_ORIGINS=http://localhost:3000")
        
        api_key = input("\nEnter your OpenAI API key (or press Enter to continue without): ")
        if api_key.strip():
            with open(env_file, 'w') as f:
                f.write(f"OPENAI_API_KEY={api_key.strip()}\n")
                f.write("DEBUG=True\n")
                f.write("CORS_ORIGINS=http://localhost:3000\n")
            print("✅ Created .env file!")

def main():
    """Main launcher function"""
    print("🚀 HF Sheets Launcher")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        print("❌ Missing requirements. Please install Python and Node.js")
        input("Press Enter to exit...")
        return
    
    # Check .env file
    check_env_file()
    
    # Setup backend
    python_path = setup_backend()
    
    # Setup frontend  
    setup_frontend()
    
    print("\n🚀 Starting servers...")
    
    # Start backend
    backend_dir = Path("backend")
    if "conda run" in str(python_path):
        # Using conda environment
        uvicorn_cmd = f"{python_path} -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
        backend_process = run_command(uvicorn_cmd, cwd=backend_dir, shell=True)
    else:
        # Using venv or system python
        uvicorn_cmd = [str(python_path), "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
        backend_process = run_command(uvicorn_cmd, cwd=backend_dir)
    
    if not backend_process:
        print("❌ Failed to start backend server")
        return
    
    print("✅ Backend server starting on http://localhost:8000")
    
    # Wait a bit for backend to start
    time.sleep(3)
    
    # Start frontend
    frontend_dir = Path("frontend")
    npm_cmd = ["npm", "start"]
    frontend_process = run_command(npm_cmd, cwd=frontend_dir)
    
    if not frontend_process:
        print("⚠️  Could not start frontend automatically.")
        print("Please run this manually in another terminal:")
        print(f"cd {frontend_dir.absolute()}")
        print("npm start")
        frontend_process = None
    
    if frontend_process:
        print("✅ Frontend server starting on http://localhost:3000")
    else:
        print("⚠️  Frontend not started automatically - please start manually")
    
    # Wait a bit then open browser
    time.sleep(5)
    try:
        webbrowser.open("http://localhost:3000")
        print("🌐 Opening browser...")
    except:
        print("Could not open browser automatically")
    
    print("\n" + "=" * 50)
    print("🎉 HF Sheets is running!")
    print("Backend:  http://localhost:8000")
    print("Frontend: http://localhost:3000")
    print("=" * 50)
    print("\nPress Ctrl+C to stop both servers")
    
    try:
        # Wait for user to stop
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("✅ Servers stopped")

if __name__ == "__main__":
    main()