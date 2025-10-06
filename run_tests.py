#!/usr/bin/env python
"""
Script to run all tests for the Movie Booking System.

Usage:
    python run_tests.py
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_booking_system.settings')
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["users", "movies"])

    if failures:
        sys.exit(1)
    else:
        print("\n" + "="*50)
        print("All tests passed successfully!")
        print("="*50)
