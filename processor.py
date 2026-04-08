"""
Sora Warehouse Processor - Main Entry Point
Run this file to start the warehouse management system
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.web.input_system import start_server


def _resolve_port() -> int:
    """Resolve server port from CLI arg or PORT env var; fallback to 8080."""
    if len(sys.argv) > 1:
        try:
            return int(sys.argv[1])
        except ValueError:
            pass

    port_env = os.getenv('PORT')
    if port_env:
        try:
            return int(port_env)
        except ValueError:
            pass

    return 8080

if __name__ == '__main__':
    port = _resolve_port()
    print("🚀 Starting Sora Warehouse Management System...")
    print("=" * 60)
    print(f"Using port: {port}")
    start_server(port)
