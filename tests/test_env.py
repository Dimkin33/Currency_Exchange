import os
import sys


def test_pythonpath():
    print("PYTHONPATH:", os.getenv("PYTHONPATH"))
    print("sys.path:", sys.path)
