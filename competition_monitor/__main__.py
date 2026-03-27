"""
CLI entry point for the Competition Results Monitor.

Usage:
    python -m competition_monitor                     # monitor all competitions
    python -m competition_monitor --comp "Fe14 ..."   # monitor one competition
    python -m competition_monitor --list               # list configured competitions
"""

import argparse
import sys

from competition_monitor.config import get_active_competitions, competition_url
from competition_monitor.monitor import run


def main():
    parser = argparse.ArgumentParser(
        description="Competition Results Monitor – fixtures, results & table "
                    "notifications for GAA competitions on rebelog.ie / gaacork.ie",
    )
    parser.add_argument(
        "--comp",
        dest="competition",
        help="Run only the named competition (exact match)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all configured competitions and exit",
    )
    args = parser.parse_args()

    if args.list:
        comps = get_active_competitions()
        print(f"{len(comps)} competition(s) configured:\n")
        for name, cfg in comps.items():
            print(f"  {name}")
            print(f"    URL:   {competition_url(cfg)}")
            print(f"    Topic: {cfg['ntfy_topic']}")
            print()
        sys.exit(0)

    run(competition_filter=args.competition)


if __name__ == "__main__":
    main()
