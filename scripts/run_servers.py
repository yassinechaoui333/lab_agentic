"""
scripts/run_servers.py – Launch all 5 MCP tool servers as subprocesses.
Usage:  python scripts/run_servers.py    (from project root)
Stop:   Ctrl+C  (gracefully terminates all servers)
"""

import subprocess
import sys
import signal
import time
import os

SERVERS = [
    ("travel-search-mcp", "src/mcp_servers/travel_search_server.py", 3001),
    ("finance-mcp",       "src/mcp_servers/finance_server.py",        3002),
    ("weather-mcp",       "src/mcp_servers/weather_server.py",        3003),
    ("currency-mcp",      "src/mcp_servers/currency_server.py",       3004),
    ("calculator-mcp",    "src/mcp_servers/calculator_server.py",     3005),
]

processes: list[subprocess.Popen] = []


def cleanup(*_):
    print("\n⏹  Stopping all MCP servers...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    for p in processes:
        try:
            p.wait(timeout=5)
        except Exception:
            p.kill()
    print("✅ All servers stopped.")
    sys.exit(0)


signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)


def main():
    root = os.path.dirname(os.path.abspath(__file__))

    print("🚀 Starting MCP Tool Servers...\n")
    for name, script, port in SERVERS:
        path = os.path.join(root, script)
        p = subprocess.Popen(
            [sys.executable, path],
            cwd=root,
        )
        processes.append(p)
        print(f"  ✅ {name:20s}  → http://localhost:{port}/sse  (PID {p.pid})")

    print(f"\n🟢 All {len(SERVERS)} servers running. Press Ctrl+C to stop.\n")

    # Wait for any process to exit (shouldn't happen in normal operation)
    while True:
        for i, p in enumerate(processes):
            ret = p.poll()
            if ret is not None:
                name = SERVERS[i][0]
                print(f"⚠️  {name} exited with code {ret}")
        time.sleep(2)


if __name__ == "__main__":
    main()
