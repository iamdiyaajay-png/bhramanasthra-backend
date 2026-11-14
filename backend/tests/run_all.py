"""
Master Test Runner for BHnMISnTRA Backend
NASA Space Apps Challenge 2026: Dancing with the SARs (BHnMISnTRA)
Runs all consolidated test suites using Python standard library unittest.
Verifies complete data isolation and zero modifications to persistent competition files.
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Ensure backend root is on sys.path
_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))


def get_data_footprint() -> dict:
    """Computes mtimes and sizes of all files in backend/data and backend/outputs."""
    footprint = {}
    for folder in [_backend_root / "data", _backend_root / "outputs"]:
        if folder.is_dir():
            for p in folder.rglob("*"):
                if p.is_file():
                    footprint[str(p)] = (p.stat().st_mtime, p.stat().st_size)
    return footprint


def main():
    print("=" * 75)
    print("BHnMISnTRA BACKEND CONSOLIDATED TEST SUITE")
    print("NASA Space Apps Challenge 2026: Dancing with the SARs")
    print("Running with standard library unittest in 100% isolated sandbox mode")
    print("=" * 75 + "\n")

    # 1. Snapshot persistent project data before test run
    before_footprint = get_data_footprint()
    start_time = time.time()

    # 2. Discover and execute all test modules
    tests_dir = Path(__file__).resolve().parent
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(tests_dir),
        pattern="test_*.py",
        top_level_dir=str(_backend_root),
    )

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    # 3. Snapshot persistent project data after test run
    after_footprint = get_data_footprint()

    # 4. Strict Data Integrity Verification
    data_intact = True
    data_anomalies = []

    # Check for modified or deleted files
    for file_path, (mtime, size) in before_footprint.items():
        if file_path not in after_footprint:
            data_intact = False
            data_anomalies.append(f"Deleted file: {file_path}")
        elif after_footprint[file_path] != (mtime, size):
            data_intact = False
            data_anomalies.append(f"Modified file: {file_path}")

    # Check for newly created files
    for file_path in after_footprint:
        if file_path not in before_footprint:
            data_intact = False
            data_anomalies.append(f"Unexpected new file: {file_path}")

    # 5. Print Executive Summary
    print("\n" + "=" * 75)
    print("EXECUTIVE TEST RUN SUMMARY")
    print("=" * 75)
    print(f"Total Test Cases Run:   {result.testsRun}")
    print(f"Successful Tests:       {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed Tests:           {len(result.failures)}")
    print(f"Errors:                 {len(result.errors)}")
    print(f"Execution Time:         {elapsed:.3f} seconds")
    print(f"Data Isolation Status:  {'PASS (100% Unmodified)' if data_intact else 'FAIL (Pollution Detected)'}")

    if not data_intact:
        print("\n[CRITICAL WARNING] Data Integrity Check Failed:")
        for anomaly in data_anomalies:
            print(f"  - {anomaly}")

    print("=" * 75)

    if result.wasSuccessful() and data_intact:
        print("RESULT: ALL CONSOLIDATED TESTS PASSED WITH ZERO DATA POLLUTION!\n")
        sys.exit(0)
    else:
        print("RESULT: TESTS FAILED OR DATA INTEGRITY COMPROMISED.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

