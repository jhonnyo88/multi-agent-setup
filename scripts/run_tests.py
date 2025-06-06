#!/usr/bin/env python3
"""
Test Runner Script for DigiNativa AI Team
========================================

Runs different test suites with appropriate configurations.
"""

import sys
import subprocess
from pathlib import Path

def run_github_integration_tests():
    """Run GitHub integration tests."""
    print("🧪 Running GitHub Integration Tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_github_integration/", 
        "-v", "--tb=short"
    ], cwd=Path(__file__).parent.parent)
    
    return result.returncode == 0

def run_all_tests():
    """Run all tests."""
    print("🧪 Running All Tests...")
    
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", "--tb=short"
    ], cwd=Path(__file__).parent.parent)
    
    return result.returncode == 0

def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "github":
            success = run_github_integration_tests()
        elif sys.argv[1] == "all":
            success = run_all_tests()
        else:
            print("Usage: python scripts/run_tests.py [github|all]")
            sys.exit(1)
    else:
        success = run_github_integration_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()