#!/usr/bin/env python3
"""Compatibility entry point for the canonical Grammar lambda engine."""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    runpy.run_module("imscrbgrmr.lambda_engine", run_name="__main__")
else:
    from imscrbgrmr.lambda_engine import *
