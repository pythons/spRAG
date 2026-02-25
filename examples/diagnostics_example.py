"""
Example: run dsRAG diagnostics for setup checks.
"""

from pprint import pprint

from dsrag import run_diagnostics


if __name__ == "__main__":
    pprint(run_diagnostics())
