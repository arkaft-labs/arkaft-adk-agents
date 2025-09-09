#!/usr/bin/env python3
"""
Test Runner for ADK Agents

Runs all ADK agent tests from the new location.
"""

import sys
import os
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_all_tests():
    """Run all ADK agent tests."""
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)