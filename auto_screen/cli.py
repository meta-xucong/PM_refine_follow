from __future__ import annotations

import argparse
import json

from .config import load_config, resolve_path
from .housekeeping import perform_storage_cleanup
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

    reset = sub.add_parser("start-fresh-round", help="Preserve history but reset the current candidate queue")
    reset.add_argument(
        "--keep-pending-alerts",
        action="store_true",
        help="Do not mark old pending ServerChan alerts as superseded",
    )

    sub.add_parser("status", help="Print state DB status")
    cleanup = sub.add_parser("cleanup", help="Run one storage cleanup pass")
    cleanup.add_argument("--light", action="store_true", help="Skip SQLite pruning/vacuum")
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
    if args.command == "start-fresh-round":
        store = StateStore(resolve_path(config, "state_db"))
        try:
            print(
                json.dumps(
                    store.start_fresh_candidate_round(supersede_pending_alerts=not args.keep_pending_alerts),
                    ensure_ascii=False,
                    indent=2,
                )
            )
        finally:
            store.close()
        return
    if args.command == "cleanup":
        result = perform_storage_cleanup(config, reason="cli", include_sqlite=not args.light)
        print(json.dumps(result, ensure_ascii=False, indent=2))
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
