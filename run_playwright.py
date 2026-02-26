import subprocess
import os
from datetime import datetime
from pathlib import Path

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def run_tests():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = REPORTS_DIR / f"run_{timestamp}.log"

    command = ["npx.cmd" if os.name == "nt" else "npx", "playwright", "test"]

    with open(log_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            command,
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd=os.getcwd(),
            env={**os.environ, "CI": "1"}
        )
        process.wait()

    return log_file.name, process.returncode