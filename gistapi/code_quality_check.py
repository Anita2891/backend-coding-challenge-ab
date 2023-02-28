import os
import subprocess

project_dir = os.getcwd()

# List all Python files in the project directory
python_files = [os.path.join(dirpath, filename)
                for dirpath, _, filenames in os.walk(project_dir)
                for filename in filenames
                if filename.endswith(".py")]

# Run code quality tools on each Python file
for python_file in python_files:
    print(f"Checking file {python_file}...")

    # Run Flake8 - style guide enforcer
    subprocess.run(["flake8", python_file])

    # Run Pylint- coding standards check and errors check
    subprocess.run(["pylint", python_file])

    # Run Black-code formatter
    subprocess.run(["black", python_file])