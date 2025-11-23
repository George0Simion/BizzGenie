#!/usr/bin/env python3
import subprocess
import sys
import time
import pathlib
import signal

ROOT = pathlib.Path(__file__).resolve().parent

processes: list[tuple[str, subprocess.Popen]] = []


def start(name: str, cmd: list[str]):
    """Start a service as a background process."""
    print(f"▶️  Starting {name}: {' '.join(cmd)}")
    p = subprocess.Popen(cmd, cwd=ROOT)
    processes.append((name, p))


def main():
    try:
        # 1️⃣ Inventory agent (Flask on 5002)
        # agents/inventory_agent.py contains the Flask app & init_db
        start("inventory", [sys.executable, "agents/inventory_agent.py"])

        # 2️⃣ Legal agent (Flask on 5003)
        # file name in your repo screenshot: legal_placeholder.py
        start("legal", [sys.executable, "legal_placeholder.py"])

        # 3️⃣ Orchestrator (Flask on 5001)
        start("orchestrator", [sys.executable, "orchestrator.py"])

        # 4️⃣ Finance API (FastAPI on 5004)
        # Uses uvicorn to serve backend/financeAPI.py:app
        start(
            "finance",
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.financeAPI:app",
                "--port",
                "5004",
                "--reload",
            ],
        )

        print("⏳ Giving services a few seconds to start...")
        time.sleep(7)

        # 5️⃣ Run unified tests (including finance + end-to-end)
        print("🧪 Running tests/test.py ...")
        test_proc = subprocess.run(
            [sys.executable, "tests/test.py"],
            cwd=ROOT,
        )
        if test_proc.returncode != 0:
            print(f"❌ Tests failed with code {test_proc.returncode}")
        else:
            print("✅ Tests passed.")

        print("\nAll services are running. Press Ctrl+C to stop them.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt received, stopping all services...")
    finally:
        for name, p in processes:
            if p.poll() is None:
                print(f"🔻 Terminating {name} (pid={p.pid})")
                p.terminate()

        # Give them a moment to exit cleanly
        time.sleep(2)
        for name, p in processes:
            if p.poll() is None:
                print(f"⚠️  {name} still running, killing...")
                p.kill()


if __name__ == "__main__":
    main()
