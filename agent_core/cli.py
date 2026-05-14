from __future__ import annotations

import argparse
import json
from pathlib import Path

from .candidate_reviewer import review_analysis_file
from .config import load_config, resolve_path
from .daily_planner import build_daily_plan
from .feedback import import_feedback_file
from .memory_store import AgentMemoryStore


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polymarket AI Agent Core")
    parser.add_argument("--config", default="agent_core_config.example.json", help="Agent config JSON path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show Agent memory status")

    review = sub.add_parser("review", help="Review one account_analysis.json")
    review.add_argument("--analysis", required=True, help="Path to account_analysis.json")
    review.add_argument("--dry-run", action="store_true", help="Do not write Agent memory")

    feedback = sub.add_parser("feedback", help="Import feedback file")
    feedback_sub = feedback.add_subparsers(dest="feedback_command", required=True)
    import_json = feedback_sub.add_parser("import-json", help="Import feedback JSON/CSV")
    import_json.add_argument("--path", required=True, help="Path to feedback JSON/CSV")

    plan = sub.add_parser("plan", help="Build daily plan")
    plan_sub = plan.add_subparsers(dest="plan_command", required=True)
    daily = plan_sub.add_parser("daily", help="Build advisory daily plan")
    daily.add_argument("--dry-run", action="store_true", help="Print only")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.command == "status":
        store = AgentMemoryStore(resolve_path(config, "memory_db"))
        try:
            print(json.dumps(store.status(), ensure_ascii=False, indent=2))
        finally:
            store.close()
        return

    if args.command == "review":
        store = None if args.dry_run else AgentMemoryStore(resolve_path(config, "memory_db"))
        try:
            review = review_analysis_file(
                Path(args.analysis),
                config,
                memory_store=store,
                dry_run=args.dry_run,
            )
            print(json.dumps(review, ensure_ascii=False, indent=2))
        finally:
            if store is not None:
                store.close()
        return

    if args.command == "feedback":
        schema_path = resolve_path(config, "schema_dir") / "feedback_event.schema.json"
        store = AgentMemoryStore(resolve_path(config, "memory_db"))
        try:
            result = import_feedback_file(args.path, schema_path=schema_path, memory_store=store)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        finally:
            store.close()
        return

    if args.command == "plan" and args.plan_command == "daily":
        plan = build_daily_plan({}, config)
        print(json.dumps(plan, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

