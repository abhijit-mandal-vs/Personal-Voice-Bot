"""Setup script for the voice bot."""

import os
import subprocess
import sys
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 9)
    current_version = sys.version_info

    if current_version < required_version:
        print(
            f"Error: Python {required_version[0]}.{required_version[1]} or higher is required."
        )
        print(
            f"Current Python version: {current_version[0]}.{current_version[1]}.{current_version[2]}"
        )
        sys.exit(1)

    print(
        f"Python version check passed: {current_version[0]}.{current_version[1]}.{current_version[2]}"
    )


def check_pip():
    """Check if pip is installed."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("Pip is installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: pip is not installed or not working correctly.")
        return False


def create_virtual_environment():
    """Create a virtual environment."""
    try:
        # Check if venv module is available
        subprocess.run(
            [sys.executable, "-m", "venv", "--help"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Create virtual environment
        venv_path = Path("venv")
        if venv_path.exists():
            print("Virtual environment already exists. Skipping creation.")
        else:
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("Virtual environment created successfully.")

        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Could not create virtual environment.")
        return False


def install_dependencies():
    """Install dependencies from requirements.txt."""
    try:
        print("Installing dependencies...")

        # Determine the pip executable based on the virtual environment
        if os.name == "nt":  # Windows
            pip_executable = os.path.join("venv", "Scripts", "pip")
        else:  # Unix/Linux/MacOS
            pip_executable = os.path.join("venv", "bin", "pip")

        # Upgrade pip
        subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)

        # Install requirements
        subprocess.run(
            [pip_executable, "install", "-r", "requirements.txt"], check=True
        )

        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies.")
        return False


def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")
    env_example_path = Path(".env.example")

    if env_path.exists():
        print(".env file already exists. Skipping creation.")
        return

    print("Creating .env file...")
    if env_example_path.exists():
        shutil.copy(env_example_path, env_path)
    else:
        with open(env_path, "w") as f:
            f.write("# OpenAI API Key\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n\n")
            f.write("# Application Settings\n")
            f.write("APP_NAME=Personal Voice Bot\n")
            f.write("APP_ENV=development\n")
            f.write("DEBUG=True\n\n")
            f.write("# API Settings\n")
            f.write("API_HOST=0.0.0.0\n")
            f.write("API_PORT=8000\n\n")
            f.write("# Streamlit Settings\n")
            f.write("STREAMLIT_SERVER_PORT=8501\n")
            f.write("STREAMLIT_SERVER_HEADLESS=True\n")

    print(".env file created. Please edit it to add your OpenAI API key.")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print("\nNext steps:")

    # Determine activation command based on OS
    if os.name == "nt":  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/MacOS
        activate_cmd = "source venv/bin/activate"

    print(f"1. Activate the virtual environment: {activate_cmd}")
    print("2. Edit the .env file to add your OpenAI API key")
    print("3. Start the API server: uvicorn app.main:app --reload")
    print(
        "4. In a new terminal, start the Streamlit frontend: streamlit run app/frontend/main.py"
    )
    print("\nEnjoy your Personal Voice Bot!")


def main():
    """Main setup function."""
    print("Starting setup for Personal Voice Bot...")

    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Run setup steps
    check_python_version()
    if not check_pip():
        sys.exit(1)

    if not create_virtual_environment():
        sys.exit(1)

    if not install_dependencies():
        sys.exit(1)

    create_env_file()
    print_next_steps()


if __name__ == "__main__":
    main()
