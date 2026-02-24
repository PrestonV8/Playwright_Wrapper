import os
import argparse
import subprocess
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="Run Playwright tests with optional env + suite filter.")
    parser.add_argument("--env", default="staging", help="Environment name (e.g., qa, staging, prod). Default: staging")
    parser.add_argument("--suite", default="", help='Suite name to filter by test title (e.g., "smoke", "login"). Default: run all tests')
    parser.add_argument("--headed", action="store_true", help="Run in headed mode (default is headless).")

    args = parser.parse_args()

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    # This becomes a run-specific folder so reports never overwrite
    report_dir = f"reports/{args.env}/{run_id}"

    # Base command: run tests + save html report to a unique folder
    cmd_parts = [
        "npx playwright test",
        f'--reporter=html',
        f'--output="{report_dir}"'
    ]

    # Optional: filter tests by name (works great for "smoke", "login", etc.)
    if args.suite.strip():
        # NOTE: this matches test titles, so name tests like: test("smoke: login works", ...)
        cmd_parts.append(f'--grep "{args.suite}"')

    # Optional: headed mode
    if args.headed:
        cmd_parts.append("--headed")

    # Pass ENV to Playwright tests (your tests can read process.env.ENV)
    # On Windows, easiest is to set it inline for this command:
    full_cmd = " ".join(cmd_parts)

    # Create environment copy and inject ENV variable
    env = os.environ.copy()
    env["ENV"] = args.env

    print(f"\nRunning: {full_cmd}\n")

    result = subprocess.run(
        full_cmd,
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )

    print(result.stdout)
    print(result.stderr)

    # IMPORTANT: make CI fail when tests fail
    raise SystemExit(result.returncode)

if __name__ == "__main__":
    main()
