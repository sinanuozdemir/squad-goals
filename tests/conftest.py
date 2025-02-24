import os
import subprocess
import sys
import venv
import shutil

import pytest


@pytest.fixture(scope="session", autouse=True)
def local_env():
    """Create a temporary virtual environment and install local squad_goals."""
    env_dir = os.path.join(os.getcwd(), "test_env")
    
    # Delete existing test_env directory if it exists
    if os.path.exists(env_dir):
        shutil.rmtree(env_dir)
    
    # Create new virtual environment
    venv.create(env_dir, with_pip=True)
    python_executable = os.path.join(env_dir, "bin", "python") if sys.platform != "win32" else os.path.join(env_dir,
                                                                                                            "Scripts",
                                                                                                            "python.exe")

    # Install squad_goals in the virtual environment
    subprocess.run([python_executable, "-m", "pip", "install", "-e", "."], check=True)

    # Modify sys.path to prioritize the local virtual environment
    sys.path.insert(0, os.path.join(env_dir, "lib", f"python{sys.version_info.major}.{sys.version_info.minor}",
                                    "site-packages"))

    yield  # Run tests

    # Cleanup after tests
    subprocess.run(["rm", "-rf", env_dir], check=True) if sys.platform != "win32" else subprocess.run(
        ["rmdir", "/s", "/q", env_dir], shell=True)
