# alert.py
import sys
import subprocess
import time
import platform

if len(sys.argv) < 2:
    print("Usage: python alert.py <script_to_run.py> [args...]")
    sys.exit(1)

script_to_run = sys.argv[1]
script_args = sys.argv[2:]

# Run the target script
result = subprocess.run([sys.executable, script_to_run] + script_args)

# Play beep / alert depending on OS
if platform.system() == "Windows":
    import winsound
    winsound.Beep(1000, 500)  # 1000 Hz, 0.5 sec
elif platform.system() == "Darwin":  # macOS
    subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"])
else:  # Linux
    print("\a")  # terminal beep

# Optionally print exit code
print(f"Script {script_to_run} finished with code {result.returncode}")