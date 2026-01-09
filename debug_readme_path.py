import os
import sys

# Simulate the location of app/routers/system.py
# We are currently in root.
# Let's define the path as if we were in that file.
target_file = os.path.abspath(os.path.join("app", "routers", "system.py"))
print(f"Simulated __file__: {target_file}")

current_dir = os.path.dirname(target_file)
print(f"Directory of system.py: {current_dir}")

# My logic in system.py:
# project_root = os.path.dirname(os.path.dirname(current_dir))

step1 = os.path.dirname(current_dir)
print(f"Step 1 (up from routers): {step1}")

step2 = os.path.dirname(step1)
print(f"Step 2 (up from app): {step2}")

readme_path = os.path.join(step2, "README.md")
print(f"Calculated README path: {readme_path}")
print(f"Exists? {os.path.exists(readme_path)}")

# Also try to read it
if os.path.exists(readme_path):
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            print("Successfully opened README.md")
            print(f"First 50 chars: {f.read(50)}")
    except Exception as e:
        print(f"Error opening file: {e}")
else:
    print("File does not exist at calculated path.")
