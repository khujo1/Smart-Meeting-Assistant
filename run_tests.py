#!/usr/bin/env python3
"""
Simple test runner for Smart Meeting Assistant
"""

import os
import sys
import subprocess

def run_tests():
    """Run all tests and display results"""
    print("🧪 Running Smart Meeting Assistant Test Suite...")
    print("=" * 60)
    
    # Change to tests directory
    test_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    try:
        # Run comprehensive tests
        result = subprocess.run([
            sys.executable, 'test_comprehensive.py'
        ], cwd=test_dir, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed.")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
