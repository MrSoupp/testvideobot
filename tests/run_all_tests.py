#!/usr/bin/env python3
"""
Master test runner - runs all tests and generates report
"""
import subprocess
import sys
from datetime import datetime


def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n{'=' * 80}")
    print(f"Running: {description}")
    print(f"{'=' * 80}")
    try:
        result = subprocess.run(command, shell=True, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False


def main():
    """Run all tests"""
    print(f"\n{'=' * 80}")
    print("VIDEO ANALYTICS BOT - COMPREHENSIVE TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}")

    tests = [
        ("python test_db_connectivity.py", "Database Connectivity Test"),
        ("python test_sql_queries.py", "SQL Query Functionality Test"),
        ("python test_user_requests.py", "User Request Scenarios Test"),
    ]

    results = []
    for command, description in tests:
        success = run_command(command, description)
        results.append((description, success))

    # Print summary
    print(f"\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")

    passed = 0
    failed = 0

    for test_name, success in results:
        status = "[PASSED]" if success else "[FAILED]"
        print(f"{status} {test_name}")
        if success:
            passed += 1
        else:
            failed += 1

    print(f"\n{'=' * 80}")
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'=' * 80}\n")

    if failed == 0:
        print("All tests PASSED! System is ready for production.")
        return 0
    else:
        print(f"Some tests FAILED! Review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
