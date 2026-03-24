"""CLI for lightweight ARGOS checks."""

from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="ARGOS command line interface")
    parser.add_argument(
        "command",
        choices=["phase0-status"],
        help="Command to run",
    )
    args = parser.parse_args()

    if args.command == "phase0-status":
        print("ARGOS Phase 0 foundation is initialized.")
