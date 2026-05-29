from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import resolve_path


PHASE_LABELS = {
    "idle": "空闲",
    "cycle_started": "启动新周期",
    "housekeeping": "自动清理",
    "scanning_leaderboard": "扫描排行榜",
    "leaderboard_scanned": "排行榜扫描完成",
    "saving_candidates": "保存候选池",
    "processing_batch": "准备处理候选",
    "prefiltering": "预筛账号",
    "prefilter_passed": "预筛通过",
    "prefilter_skipped": "预筛跳过",
    "collecting_account": "拉取账号数据",
    "scoring_account": "账号打分",
    "reviewing_agent": "Agent 复核",
    "alerting": "推送候选",
    "account_failed": "账号处理失败",
    "account_done": "账号处理完成",
    "cycle_done": "周期完成",
    "cycle_failed": "周期失败",
    "sleeping": "等待下一轮",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_progress_path(config: dict[str, Any]) -> Path:
    configured = config.get("progress_path")
    if configured:
        path = Path(str(configured)).expanduser()
        return path if path.is_absolute() else Path.cwd() / path
    return resolve_path(config, "data_dir") / "progress.json"


class ProgressReporter:
    def __init__(self, path: str | Path, emit_log: bool = True) -> None:
        self.path = Path(path)
        self.emit_log = emit_log
        self.sequence = 0

    @classmethod
    def from_config(cls, config: dict[str, Any], emit_log: bool = True) -> "ProgressReporter":
        return cls(resolve_progress_path(config), emit_log=emit_log)

    def update(self, phase: str, message: str = "", **fields: Any) -> dict[str, Any]:
        self.sequence += 1
        event = {
            "phase": phase,
            "phase_label": PHASE_LABELS.get(phase, phase),
            "message": message,
            "updated_at": utc_now(),
            "updated_ts": time.time(),
            "sequence": self.sequence,
            **fields,
        }
        previous = self._read_previous()
        history = [] if phase == "cycle_started" else list(previous.get("history") or [])
        history.append({k: v for k, v in event.items() if k != "history"})
        event["history"] = history[-20:]
        self._write_atomic(event)
        if self.emit_log:
            account = fields.get("current_account")
            suffix = f" account={account}" if account else ""
            print(f"[progress] {event['phase_label']} - {message}{suffix}", flush=True)
        return event

    def _read_previous(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _write_atomic(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(event, ensure_ascii=False, indent=2)
        last_error: OSError | None = None
        for attempt in range(8):
            tmp = self.path.with_name(f"{self.path.name}.{os.getpid()}.{self.sequence}.{attempt}.tmp")
            try:
                tmp.write_text(raw, encoding="utf-8")
                tmp.replace(self.path)
                return
            except OSError as exc:
                last_error = exc
                try:
                    tmp.unlink(missing_ok=True)
                except OSError:
                    pass
                time.sleep(min(1.0, 0.1 * (attempt + 1)))
        if last_error is not None:
            raise last_error
