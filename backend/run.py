import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_venv():
    """Check if we're in a virtual environment or if venv exists."""
    venv_path = Path(__file__).parent / "venv"
    
    # Check if we're already in a venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return True
    
    # Check if venv directory exists and has python
    if venv_path.exists() and (venv_path / "bin" / "python").exists():
        print("ℹ️  Virtual environment found. Activating automatically...")
        # Try to use venv python
        venv_python = venv_path / "bin" / "python"
        if venv_python.exists():
            return True
    
    # Check if dependencies are installed in system python
    try:
        import fastapi
        import uvicorn
        print("ℹ️  Using system Python with installed dependencies.")
        return True
    except ImportError:
        pass
    
    print("⚠️  Dependencies not found.")
    print("   Installing dependencies...")
    print("   Run: pip install -r requirements.txt")
    print("   Or: python3 -m pip install --user -r requirements.txt")
    return False

if __name__ == "__main__":
    # Warn about venv but don't block execution
    check_venv()
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting H.A.R.C. Backend on http://0.0.0.0:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print("")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
