#!/usr/bin/env python3

import sys
import time
import requests
from datetime import datetime


def check_web():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✓ Web service: OK")
            return True
        else:
            print(f"✗ Web service: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Web service: {str(e)}")
        return False


def check_database():
    try:
        response = requests.get("http://localhost:8000/health/db", timeout=5)
        if response.status_code == 200:
            print("✓ Database: OK")
            return True
        else:
            print(f"✗ Database: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Database: {str(e)}")
        return False


def check_redis():
    try:
        response = requests.get("http://localhost:8000/health/redis", timeout=5)
        if response.status_code == 200:
            print("✓ Redis: OK")
            return True
        else:
            print(f"✗ Redis: Status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Redis: {str(e)}")
        return False


def main():
    print(f"Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    checks = [
        check_web,
        check_database,
        check_redis,
    ]

    results = [check() for check in checks]

    print("=" * 50)
    if all(results):
        print("All health checks passed!")
        sys.exit(0)
    else:
        print("Some health checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
