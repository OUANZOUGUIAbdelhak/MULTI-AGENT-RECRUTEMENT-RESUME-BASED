"""
Quick start script to run the Streamlit application
"""
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    app_path = Path(__file__).parent / "src" / "app" / "app.py"
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        print("\nPlease make sure Streamlit is installed:")
        print("  pip install streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
        sys.exit(0)

