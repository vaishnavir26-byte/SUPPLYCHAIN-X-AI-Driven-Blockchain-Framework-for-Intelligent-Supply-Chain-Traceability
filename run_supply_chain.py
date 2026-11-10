#!/usr/bin/env python3
"""
Launcher script for the AI and Blockchain-Based Supply Chain Platform.
Usage:
    python3 run_supply_chain.py
    python3 run_supply_chain.py --port 8080
    python3 run_supply_chain.py --test
"""

import sys
import os

# Ensure supply_chain package is on path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

if "--test" in sys.argv:
    import unittest
    from supply_chain.test_system import TestSupplyChainBlockchainAI
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSupplyChainBlockchainAI)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

port = 8000
for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        port = int(sys.argv[i + 1])

from supply_chain.server import start_server

if __name__ == "__main__":
    print("=" * 70)
    print("   AI & Blockchain-Based Supply Chain Traceability & Risk Platform")
    print("   Version: 1.0 (Simulated Hyperledger Fabric & Raft Architecture)")
    print("=" * 70)
    print(f" Web Dashboard & REST API: http://localhost:{port} (or http://127.0.0.1:{port})")
    print(" Preserving Zero-IoT Hardware Constraint (Pure Cryptographic Verification)")
    print(" Press Ctrl+C to terminate.")
    print("=" * 70)
    start_server(port)
