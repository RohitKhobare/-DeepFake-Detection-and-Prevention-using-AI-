#!/usr/bin/env python
"""
Launcher script for DeepFake Detection Pro - Website Style
Run this script to start the modern website-style application
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the website-style application"""

    # Get the project root directory
    project_root = Path(__file__).parent

    # Path to the website app
    app_path = project_root / "Code" / "app_website.py"

    if not app_path.exists():
        print("❌ Error: app_website.py not found!")
        print(f"Expected path: {app_path}")
        sys.exit(1)

    print("🚀 Starting DeepFake Detection Pro - Website Style...")
    print("🎨 Multiple themes available: Default, Dark, Nature, Sunset, Ocean")
    print("📱 Opening at: http://localhost:8505")
    print("❌ Press Ctrl+C to stop the application")
    print("-" * 60)

    try:
        # Launch Streamlit with the website app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(app_path),
            "--server.port", "8505",
            "--server.headless", "true"
        ], check=True)

    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: Streamlit not found. Please install with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()