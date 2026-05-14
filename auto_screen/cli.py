from __future__ import annotations

import argparse
import json

from .config import load_config, resolve_path
from .scheduler import run_forever, run_once
from .state_store import StateStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polymarket leaderboard auto-screening runner")
    parser.add_argument("--config", default=None, help="Optional JSON config path")
    sub = parser.add_subparsers(dest="command", required=True)

    once = sub.add_parser("once", help="Run one scan/process cycle")
    once.add_argument("--limit-candidates", type=int, default=None, help="Max candidates to scan in this run")
    once.add_argument("--process-limit", type=int, default=None, help="Max pending candidates to process")
    once.add_argument("--dry-run-alerts", action="store_true", help="Do not send ServerChan; return dry-run payloads")
    once.add_argument("--prefilter-only", action="store_true", help="Only scan + shallow prefilter; skip full collection/scoring")

    run = sub.add_parser("run", help="Run forever")
    run.add_argument("--dry-run-alerts", action="store_true", help="Do not send ServerChan")

    sub.add_parser("status", help="Print state DB status")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.command == "status":
        store = StateStore(resolve_path(config, "state_db"))
        try:
            print(json.dumps(store.status(), ensure_ascii=False, indent=2))
        finally:
            store.close()
        return
    if args.command == "once":
        stats = run_once(
            config,
            limit_candidates=args.limit_candidates,
            process_limit=args.process_limit,
            dry_run_alerts=args.dry_run_alerts,
            prefilter_only=args.prefilter_only,
        )
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return
    if args.command == "run":
        run_forever(config, dry_run_alerts=args.dry_run_alerts)


if __name__ == "__main__":
    main()
