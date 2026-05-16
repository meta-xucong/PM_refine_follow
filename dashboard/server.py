from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import signal
import sqlite3
import subprocess
import sys
import time
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


def env_path(name: str, default: str | Path) -> Path:
    value = os.environ.get(name)
    return Path(value).expanduser().resolve() if value else Path(default).expanduser().resolve()


ROOT = env_path("PM_APP_ROOT", Path(__file__).resolve().parents[1])
STATIC_DIR = Path(__file__).resolve().parent / "static"
DATA_DIR = env_path("PM_DATA_DIR", ROOT / "auto_screen_data")
UI_DIR = env_path("PM_UI_DIR", DATA_DIR / "dashboard")
AUTO_CONFIG = env_path("PM_AUTO_CONFIG", ROOT / "auto_screen_config.ui.json")
AGENT_CONFIG = env_path("PM_AGENT_CONFIG", ROOT / "agent_core_config.ui.json")
AUTO_CONFIG_EXAMPLE = env_path("PM_AUTO_CONFIG_EXAMPLE", ROOT / "auto_screen_config.example.json")
AGENT_CONFIG_EXAMPLE = env_path("PM_AGENT_CONFIG_EXAMPLE", ROOT / "agent_core_config.example.json")
PID_FILE = UI_DIR / "auto_screen_process.json"
LOG_FILE = env_path("PM_DASHBOARD_AUTO_LOG", UI_DIR / "auto_screen.log")


def ensure_ui_files() -> None:
    UI_DIR.mkdir(parents=True, exist_ok=True)
    if not AUTO_CONFIG.exists() and AUTO_CONFIG_EXAMPLE.exists():
        AUTO_CONFIG.write_text(AUTO_CONFIG_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    if not AGENT_CONFIG.exists() and AGENT_CONFIG_EXAMPLE.exists():
        AGENT_CONFIG.write_text(AGENT_CONFIG_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def pid_running(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    if os.name == "nt":
        proc = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            return False
        return f'"{pid}"' in proc.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def read_process_state() -> dict[str, Any]:
    state = read_json(PID_FILE, {}) or {}
    pid = int(state.get("pid") or 0)
    state["running"] = pid_running(pid)
    if not state["running"] and pid:
        state["stale"] = True
    state["log_path"] = str(LOG_FILE)
    return state


def tail_text(path: Path, lines: int = 180) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return "\n".join(text.splitlines()[-lines:])


def stop_process() -> dict[str, Any]:
    state = read_process_state()
    pid = int(state.get("pid") or 0)
    if not pid or not state.get("running"):
        return {"stopped": False, "reason": "not_running"}
    if os.name == "nt":
        proc = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, text=True)
        return {"stopped": proc.returncode == 0, "stdout": proc.stdout, "stderr": proc.stderr}
    os.kill(pid, signal.SIGTERM)
    return {"stopped": True}


def launch_auto_screen(args: list[str], mode: str) -> dict[str, Any]:
    state = read_process_state()
    if state.get("running"):
        return {"started": False, "reason": "already_running", "pid": state.get("pid")}
    ensure_ui_files()
    UI_DIR.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    popen_kwargs: dict[str, Any] = {
        "cwd": str(ROOT),
        "stdin": subprocess.DEVNULL,
        "stderr": subprocess.STDOUT,
        "text": True,
        "env": env,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    with LOG_FILE.open("a", encoding="utf-8") as log:
        log.write(f"\n\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} start {mode} ===\n")
        log.flush()
        proc = subprocess.Popen(
            [sys.executable, "-m", "auto_screen.cli", "--config", str(AUTO_CONFIG), *args],
            stdout=log,
            **popen_kwargs,
        )
    state = {
        "pid": proc.pid,
        "mode": mode,
        "command": [sys.executable, "-m", "auto_screen.cli", "--config", str(AUTO_CONFIG), *args],
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    write_json(PID_FILE, state)
    return {"started": True, **state}


def env_truthy(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def autostart_auto_screen_if_requested() -> dict[str, Any]:
    if not env_truthy("PM_AUTOSTART_SCAN", False):
        return {"autostart": False, "reason": "disabled"}
    state = read_process_state()
    if state.get("running"):
        return {"autostart": False, "reason": "already_running", "pid": state.get("pid")}
    return {"autostart": True, **launch_auto_screen(["run"], "run")}


def build_auto_screen_args(action: str, body: dict[str, Any]) -> list[str]:
    args = [action]
    if action == "once":
        if body.get("limit_candidates"):
            args.extend(["--limit-candidates", str(int(body["limit_candidates"]))])
        if body.get("process_limit"):
            args.extend(["--process-limit", str(int(body["process_limit"]))])
    if bool(body.get("dry_run_alerts", False)):
        args.append("--dry-run-alerts")
    if action == "once" and bool(body.get("prefilter_only")):
        args.append("--prefilter-only")
    return args


def sqlite_rows(db_path: Path, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA busy_timeout=10000")
        return [dict(row) for row in conn.execute(query, params).fetchall()]
    except sqlite3.Error:
        return []
    finally:
        conn.close()


def resolve_auto_path(auto_cfg: dict[str, Any], key: str, default: str) -> Path:
    value = Path(str(auto_cfg.get(key, default))).expanduser()
    if value.is_absolute():
        return value
    return ROOT / value


def mask_secret(value: str | None) -> str:
    text = str(value or "").strip()
    if not text:
        return "未设置"
    if len(text) <= 8:
        return "*" * len(text)
    return f"{text[:4]}...{text[-4:]}"


def serverchan_sendkey_file(auto_cfg: dict[str, Any]) -> Path:
    serverchan_cfg = auto_cfg.get("serverchan") or {}
    value = Path(str(serverchan_cfg.get("sendkey_file") or "~/.codex/secrets/serverchan_sendkey.txt")).expanduser()
    if value.is_absolute():
        return value
    return ROOT / value


def serverchan_key_info(auto_cfg: dict[str, Any]) -> dict[str, Any]:
    serverchan_cfg = auto_cfg.get("serverchan") or {}
    env_name = str(serverchan_cfg.get("sendkey_env") or "SCT_SENDKEY")
    env_value = os.environ.get(env_name, "").strip()
    file_path = serverchan_sendkey_file(auto_cfg)
    file_value = ""
    if file_path.exists():
        file_value = file_path.read_text(encoding="utf-8").strip()
    if env_value:
        active_source = "环境变量"
        active_masked = mask_secret(env_value)
        note = f"当前优先使用环境变量 {env_name}；保存文件不会覆盖正在生效的环境变量。"
    elif file_value:
        active_source = "本地文件"
        active_masked = mask_secret(file_value)
        note = "当前使用本地 SendKey 文件。"
    else:
        active_source = "未设置"
        active_masked = "未设置"
        note = "请输入 SendKey 并保存。"
    return {
        "env_name": env_name,
        "env_present": bool(env_value),
        "env_masked": mask_secret(env_value),
        "file_path": str(file_path),
        "file_exists": file_path.exists(),
        "file_masked": mask_secret(file_value),
        "active_source": active_source,
        "active_masked": active_masked,
        "note": note,
    }


def save_serverchan_key(auto_cfg: dict[str, Any], sendkey: str) -> dict[str, Any]:
    value = str(sendkey or "").strip()
    if not value:
        raise ValueError("SendKey 不能为空")
    path = serverchan_sendkey_file(auto_cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")
    info = serverchan_key_info(auto_cfg)
    info["saved"] = True
    return info


def _alert_label(row: dict[str, Any]) -> str:
    title = str(row.get("title") or "")
    if "｜" in title:
        label = title.split("｜")[-1].strip()
        if label:
            return label
    if "|" in title:
        label = title.split("|")[-1].strip()
        if label:
            return label
    return str(row.get("address") or "")


def compact_text(value: Any, limit: int = 500) -> str:
    text = " ".join(str(value or "").replace("\r", "\n").split())
    return text[:limit]


def _line_after_heading(message: str, heading: str) -> str:
    lines = message.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        for candidate in lines[index + 1 :]:
            text = candidate.strip()
            if text and not text.startswith("#"):
                return text
    return ""


def _message_line_value(message: str, label: str) -> str:
    prefixes = (f"- {label}：", f"{label}：", f"- {label}: ", f"{label}: ")
    for line in message.splitlines():
        text = line.strip()
        for prefix in prefixes:
            if text.startswith(prefix):
                return text[len(prefix) :].strip()
    return ""


def compact_recommendation(row: dict[str, Any], limit: int = 180) -> str:
    message = str(row.get("message") or "")
    if not message:
        return ""

    recommendation = _message_line_value(message, "系统建议")
    if not recommendation:
        recommendation = _message_line_value(message, "下一步建议")
    if not recommendation:
        recommendation = _message_line_value(message, "建议跟单方式")
    if not recommendation:
        recommendation = _line_after_heading(message, "## 操作建议")
    if not recommendation:
        recommendation = _line_after_heading(message, "## 一句话结论")

    recommendation = re.sub(r"^这个账号当前评分为[^。]*。", "", recommendation).strip()
    recommendation = re.sub(r"^当前评分[^。]*。", "", recommendation).strip()
    recommendation = recommendation.lstrip("- ").strip()
    return compact_text(recommendation, limit)


def pushed_alert_rows(db_path: Path) -> list[dict[str, Any]]:
    return sqlite_rows(
        db_path,
        """
        SELECT id, address, final_score, alert_grade, title, message, created_at, pushed_at, push_batch_id
        FROM alerts
        WHERE push_status='sent'
        ORDER BY COALESCE(pushed_at, created_at) DESC, id DESC
        """,
    )


def pushed_accounts_summary(db_path: Path) -> list[dict[str, Any]]:
    rows = pushed_alert_rows(db_path)
    grouped: dict[str, dict[str, Any]] = {}
    ordered_addresses: list[str] = []
    for row in rows:
        address = str(row.get("address") or "").lower()
        if not address:
            continue
        if address not in grouped:
            ordered_addresses.append(address)
            grouped[address] = {
                "address": address,
                "label": _alert_label(row),
                "push_count": 0,
                "latest_score": row.get("final_score"),
                "latest_grade": row.get("alert_grade"),
                "latest_pushed_at": row.get("pushed_at") or row.get("created_at"),
                "rounds": [],
            }
        grouped[address]["rounds"].append(
            {
                "score": row.get("final_score"),
                "grade": row.get("alert_grade"),
                "created_at": row.get("created_at"),
                "pushed_at": row.get("pushed_at") or row.get("created_at"),
                "batch_id": row.get("push_batch_id"),
            }
        )

    result: list[dict[str, Any]] = []
    for address in ordered_addresses:
        item = grouped[address]
        rounds = item["rounds"]
        total = len(rounds)
        for index, round_item in enumerate(rounds):
            round_item["round_number"] = total - index
        item["push_count"] = total
        item["recent_rounds"] = rounds[:3]
        item["hidden_rounds"] = rounds[3:]
        result.append(item)
    return result


def pushed_accounts_csv(auto_cfg: dict[str, Any]) -> str:
    db_path = resolve_auto_path(auto_cfg, "state_db", "auto_screen_data/state.sqlite3")
    rows = pushed_alert_rows(db_path)
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["钱包地址", "昵称", "分数", "评级", "标题", "推送批次", "入库时间", "推送时间", "描述"])
    for row in rows:
        writer.writerow(
            [
                row.get("address") or "",
                _alert_label(row),
                row.get("final_score") or "",
                row.get("alert_grade") or "",
                row.get("title") or "",
                row.get("push_batch_id") or "",
                row.get("created_at") or "",
                row.get("pushed_at") or row.get("created_at") or "",
                compact_recommendation(row),
            ]
        )
    return out.getvalue()


def scoring_history_for_addresses(db_path: Path, addresses: list[str], per_address: int = 5) -> dict[str, list[dict[str, Any]]]:
    normalized = [address.lower() for address in addresses if address]
    if not normalized or not db_path.exists():
        return {}
    placeholders = ",".join("?" for _ in normalized)
    rows = sqlite_rows(
        db_path,
        f"""
        SELECT id, address, final_score, alert_grade, decision, auto_action, created_at
        FROM runs
        WHERE status='scored'
          AND lower(address) IN ({placeholders})
        ORDER BY created_at DESC, id DESC
        """,
        tuple(normalized),
    )
    grouped: dict[str, list[dict[str, Any]]] = {address: [] for address in normalized}
    for row in rows:
        address = str(row.get("address") or "").lower()
        if len(grouped.setdefault(address, [])) >= per_address:
            continue
        grouped[address].append(
            {
                "score": row.get("final_score"),
                "grade": row.get("alert_grade"),
                "decision": row.get("decision"),
                "action": row.get("auto_action"),
                "created_at": row.get("created_at"),
            }
        )
    return grouped


def auto_state_summary(auto_cfg: dict[str, Any]) -> dict[str, Any]:
    db_path = resolve_auto_path(auto_cfg, "state_db", "auto_screen_data/state.sqlite3")
    counts = {}
    alert_push_counts = {}
    if db_path.exists():
        for row in sqlite_rows(db_path, "SELECT status, count(*) AS n FROM candidates GROUP BY status"):
            counts[row["status"]] = row["n"]
        for row in sqlite_rows(db_path, "SELECT push_status, count(*) AS n FROM alerts GROUP BY push_status"):
            alert_push_counts[row.get("push_status") or "unknown"] = row["n"]
    candidate_total_count = sum(int(value or 0) for value in counts.values())
    return {
        "db_path": str(db_path),
        "candidate_counts": counts,
        "candidate_total_count": candidate_total_count,
        "alert_push_counts": alert_push_counts,
        "latest_cycles": sqlite_rows(db_path, "SELECT * FROM cycles ORDER BY id DESC LIMIT 8"),
        "recent_runs": sqlite_rows(db_path, "SELECT * FROM runs ORDER BY id DESC LIMIT 20"),
        "recent_alerts": sqlite_rows(db_path, "SELECT * FROM alerts ORDER BY id DESC LIMIT 20"),
        "pushed_accounts": pushed_accounts_summary(db_path),
    }


def progress_next_step(phase: str, running: bool) -> str:
    if not running:
        return "点击启动常驻或单轮运行"
    mapping = {
        "cycle_started": "开始扫描排行榜分片",
        "scanning_leaderboard": "扫完候选池后进入账号预筛",
        "leaderboard_scanned": "写入候选池并持续处理 pending 地址",
        "saving_candidates": "写入完成后取待处理批次",
        "processing_batch": "逐个账号做预筛",
        "prefiltering": "通过后拉取完整账号数据",
        "prefilter_passed": "按配置进入下一个账号",
        "prefilter_skipped": "跳过后进入下一个账号",
        "collecting_account": "完成数据拉取后计算评分",
        "scoring_account": "完成评分后写入 Excel/告警",
        "reviewing_agent": "完成 Agent 复核后写入结果",
        "alerting": "推送完成后处理下一个账号",
        "account_failed": "已暂存失败原因，后续周期重试该账号",
        "account_done": "继续处理批次内下一个账号",
        "cycle_done": "进入休眠，等待下一轮",
        "sleeping": "休眠结束后重新从排行榜开始",
        "cycle_failed": "检查日志后重新启动",
    }
    return mapping.get(phase, "等待下一条进度心跳")


def leaderboard_percent(leaderboard: dict[str, Any]) -> float | None:
    try:
        max_rank = float(leaderboard.get("max_rank") or 0)
        offset = float(leaderboard.get("offset") or 0)
        page_limit = float(leaderboard.get("page_limit") or 0)
        if max_rank <= 0:
            return None
        if leaderboard.get("early_stop") or leaderboard.get("api_cap_detected"):
            shard_fraction = 1.0
        else:
            shard_fraction = min(1.0, max(0.0, (offset + page_limit) / max_rank))
        total_shards = int(leaderboard.get("total_shards") or 0)
        shard_index = int(leaderboard.get("shard_index") or 0)
        if total_shards > 0 and shard_index > 0:
            return round(min(100.0, (((shard_index - 1) + shard_fraction) / total_shards) * 100), 1)
        return round(min(100.0, shard_fraction * 100), 1)
    except (TypeError, ValueError):
        return None


def progress_summary(auto_cfg: dict[str, Any], process: dict[str, Any], auto_state: dict[str, Any]) -> dict[str, Any]:
    progress_path = resolve_auto_path(auto_cfg, "progress_path", "auto_screen_data/progress.json")
    progress = read_json(progress_path, {}) or {}
    latest_cycle = (auto_state.get("latest_cycles") or [{}])[0] if auto_state.get("latest_cycles") else {}
    age_seconds = None
    if progress.get("updated_ts"):
        age_seconds = max(0.0, time.time() - float(progress["updated_ts"]))

    running = bool(process.get("running"))
    if running and progress:
        phase = progress.get("phase")
        stale_after = 300.0
        if phase in {"cycle_done", "sleeping"}:
            scan_cfg = auto_cfg.get("scan") or {}
            sleep_seconds = float(progress.get("sleep_seconds") or scan_cfg.get("cycle_sleep_seconds") or 0)
            stale_after = max(stale_after, sleep_seconds + 120.0)
        health = "ok" if age_seconds is None or age_seconds < stale_after else "stale"
        message = progress.get("message") or "进程运行中"
    elif running:
        health = "starting"
        message = "进程运行中，等待进度心跳写入"
    else:
        health = "stopped"
        message = "扫描进程未运行"

    if latest_cycle.get("status") == "failed":
        health = "error"
        message = latest_cycle.get("note") or message

    phase = progress.get("phase") or ("running_unknown" if running else "stopped")
    phase_label = progress.get("phase_label") or ("运行中" if running else "未运行")
    stats = progress.get("stats") or {}
    leaderboard = progress.get("leaderboard")
    candidate_source = progress.get("candidate_source")
    leaderboard_scan = progress.get("leaderboard_scan") or {}
    if isinstance(leaderboard, dict) and leaderboard.get("api_cap_detected") and not leaderboard_scan:
        leaderboard_scan = {
            "requested_rank_cap": leaderboard.get("max_rank"),
            "api_cap_detected": True,
            "api_visible_cap_rank": leaderboard.get("api_cap_rank"),
            "unique_candidates": leaderboard.get("unique_candidates"),
            "latest": leaderboard,
        }
    batch_total = progress.get("batch_total")
    current_index = progress.get("current_index")
    percent = None
    if isinstance(batch_total, (int, float)) and batch_total:
        percent = min(100, max(0, round((float(current_index or 0) / float(batch_total)) * 100, 1)))
    elif isinstance(leaderboard, dict):
        percent = leaderboard_percent(leaderboard)
    elif phase in {"cycle_done", "sleeping"}:
        percent = 100

    current_account = progress.get("current_account")
    current_label = progress.get("current_label")
    if current_account:
        current_target = current_account
        current_target_hint = current_label or "正在处理该地址"
    elif isinstance(leaderboard, dict):
        current_target = "未进入账号处理"
        current_target_hint = "当前正在发现候选地址，尚未开始拉取单个地址数据"
    else:
        current_target = "-"
        current_target_hint = "等待任务进度"

    return {
        "path": str(progress_path),
        "exists": progress_path.exists(),
        "health": health,
        "phase": phase,
        "phase_label": phase_label,
        "message": message,
        "updated_at": progress.get("updated_at"),
        "age_seconds": age_seconds,
        "cycle_id": progress.get("cycle_id") or latest_cycle.get("id"),
        "latest_cycle": latest_cycle,
        "current_account": current_account,
        "current_label": current_label,
        "current_target": current_target,
        "current_target_hint": current_target_hint,
        "current_index": current_index,
        "batch_total": batch_total,
        "percent": percent,
        "stats": stats,
        "candidate_total_count": auto_state.get("candidate_total_count", 0),
        "candidate_counts": auto_state.get("candidate_counts", {}),
        "final_score": progress.get("final_score"),
        "alert_grade": progress.get("alert_grade"),
        "auto_action": progress.get("auto_action"),
        "seen_before": progress.get("seen_before"),
        "scan_prompt": progress.get("scan_prompt"),
        "leaderboard": leaderboard,
        "leaderboard_scan": leaderboard_scan,
        "candidate_source": candidate_source,
        "next_step": progress_next_step(phase, running),
        "history": list(reversed((progress.get("history") or [])[-20:])),
    }


def agent_state_summary(agent_cfg: dict[str, Any]) -> dict[str, Any]:
    db_path = ROOT / str(agent_cfg.get("memory_db", "auto_screen_data/agent_memory.sqlite3"))
    if Path(str(agent_cfg.get("memory_db", ""))).is_absolute():
        db_path = Path(str(agent_cfg["memory_db"]))
    tables = {
        "agent_decisions": "SELECT count(*) AS n FROM agent_decisions",
        "user_feedback": "SELECT count(*) AS n FROM user_feedback",
        "candidate_snapshots": "SELECT count(*) AS n FROM candidate_snapshots",
        "followup_outcomes": "SELECT count(*) AS n FROM followup_outcomes",
    }
    counts = {}
    if db_path.exists():
        for key, query in tables.items():
            rows = sqlite_rows(db_path, query)
            counts[key] = rows[0]["n"] if rows else 0
    return {
        "memory_db": str(db_path),
        "counts": counts,
        "recent_decisions": sqlite_rows(db_path, "SELECT * FROM agent_decisions ORDER BY id DESC LIMIT 20"),
        "recent_feedback": sqlite_rows(db_path, "SELECT * FROM user_feedback ORDER BY id DESC LIMIT 20"),
    }


def excel_sidecar_summary(auto_cfg: dict[str, Any]) -> dict[str, Any]:
    excel_path = resolve_auto_path(auto_cfg, "excel_path", "auto_screen_data/polymarket_candidates.xlsx")
    sidecar = excel_path.with_suffix(excel_path.suffix + ".json")
    data = read_json(sidecar, {}) or {}
    return {
        "excel_path": str(excel_path),
        "sidecar_path": str(sidecar),
        "sheet_counts": {k: len(v or []) for k, v in data.items()},
        "alerts": list(reversed((data.get("alerts") or [])[-20:])),
        "all_scored": list(reversed((data.get("all_scored") or [])[-30:])),
        "agent_reviews": list(reversed((data.get("agent_reviews") or [])[-30:])),
        "skipped": list(reversed((data.get("skipped") or [])[-20:])),
    }


def list_accounts(auto_cfg: dict[str, Any], limit: int = 60) -> list[dict[str, Any]]:
    data_dir = resolve_auto_path(auto_cfg, "data_dir", "auto_screen_data")
    accounts_dir = data_dir / "accounts"
    if not accounts_dir.exists():
        return []
    rows = []
    account_dirs = [p for p in sorted(accounts_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True) if p.is_dir()]
    account_dirs = account_dirs[:limit]
    history = scoring_history_for_addresses(
        resolve_auto_path(auto_cfg, "state_db", "auto_screen_data/state.sqlite3"),
        [p.name for p in account_dirs],
    )
    for account_dir in account_dirs:
        if not account_dir.is_dir():
            continue
        analysis = read_json(account_dir / "account_analysis.json", {}) or {}
        review = read_json(account_dir / "agent_review.json", {}) or {}
        rows.append(
            {
                "address": account_dir.name,
                "label": analysis.get("account_label") or account_dir.name,
                "final_score": analysis.get("final_score"),
                "alert_grade": analysis.get("alert_grade"),
                "auto_action": analysis.get("auto_action"),
                "decision": analysis.get("decision"),
                "seen_before": analysis.get("seen_before"),
                "scan_prompt": analysis.get("scan_prompt"),
                "agent_verdict": review.get("agent_verdict") or analysis.get("agent_verdict"),
                "agent_confidence": review.get("confidence") or analysis.get("agent_confidence"),
                "data_quality_score": analysis.get("data_quality_score"),
                "pnl_quality_score": analysis.get("pnl_quality_score"),
                "copy_capacity_score": analysis.get("copy_capacity_score"),
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(account_dir.stat().st_mtime)),
                "analysis_path": str(account_dir / "account_analysis.json"),
                "agent_review_path": str(account_dir / "agent_review.json") if (account_dir / "agent_review.json").exists() else "",
                "report_zh": str(account_dir / "report_zh.md") if (account_dir / "report_zh.md").exists() else "",
                "score_history": history.get(account_dir.name.lower(), []),
            }
        )
        if len(rows) >= limit:
            break
    return rows


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/"):
                self.handle_api_get(parsed.path, parse_qs(parsed.query))
                return
            if parsed.path == "/":
                self.path = "/index.html"
            return super().do_GET()
        except Exception as exc:
            self.write_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/"):
                body = self.read_body_json()
                self.handle_api_post(parsed.path, body)
                return
            self.write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self.write_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def read_body_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def handle_api_get(self, path: str, query: dict[str, list[str]]) -> None:
        ensure_ui_files()
        auto_cfg = read_json(AUTO_CONFIG, {}) or {}
        agent_cfg = read_json(AGENT_CONFIG, {}) or {}
        if path == "/api/config":
            self.write_json({"auto_config": auto_cfg, "agent_config": agent_cfg, "paths": {"auto_config": str(AUTO_CONFIG), "agent_config": str(AGENT_CONFIG)}})
            return
        if path == "/api/serverchan-key":
            self.write_json(serverchan_key_info(auto_cfg))
            return
        if path == "/api/status":
            process = read_process_state()
            auto_state = auto_state_summary(auto_cfg)
            self.write_json(
                {
                    "process": process,
                    "progress": progress_summary(auto_cfg, process, auto_state),
                    "auto": auto_state,
                    "agent": agent_state_summary(agent_cfg),
                    "excel": excel_sidecar_summary(auto_cfg),
                }
            )
            return
        if path == "/api/export/pushed.csv":
            raw = ("\ufeff" + pushed_accounts_csv(auto_cfg)).encode("utf-8")
            self.send_response(int(HTTPStatus.OK))
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="polymarket_pushed_scores.csv"')
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if path == "/api/accounts":
            limit = int((query.get("limit") or ["60"])[0])
            self.write_json({"accounts": list_accounts(auto_cfg, limit=limit)})
            return
        if path == "/api/process":
            process = read_process_state()
            auto_state = auto_state_summary(auto_cfg)
            self.write_json(
                {
                    "process": process,
                    "progress": progress_summary(auto_cfg, process, auto_state),
                    "log_tail": tail_text(LOG_FILE),
                }
            )
            return
        self.write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def handle_api_post(self, path: str, body: dict[str, Any]) -> None:
        ensure_ui_files()
        if path == "/api/config":
            if "auto_config" in body:
                write_json(AUTO_CONFIG, body["auto_config"])
            if "agent_config" in body:
                write_json(AGENT_CONFIG, body["agent_config"])
            self.write_json({"saved": True, "paths": {"auto_config": str(AUTO_CONFIG), "agent_config": str(AGENT_CONFIG)}})
            return
        if path == "/api/serverchan-key":
            try:
                self.write_json(save_serverchan_key(read_json(AUTO_CONFIG, {}) or {}, str(body.get("sendkey") or "")))
            except ValueError as exc:
                self.write_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if path == "/api/start":
            args = build_auto_screen_args("run", body)
            self.write_json(launch_auto_screen(args, "run"))
            return
        if path == "/api/run-once":
            args = build_auto_screen_args("once", body)
            self.write_json(launch_auto_screen(args, "once"))
            return
        if path == "/api/stop":
            self.write_json(stop_process())
            return
        self.write_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)

    def write_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PM refine follow local dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_ui_files()
    autostart = autostart_auto_screen_if_requested()
    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Dashboard: http://{args.host}:{args.port}")
    if autostart.get("autostart"):
        print(f"Auto screen autostarted: pid={autostart.get('pid')}")
    server.serve_forever()


if __name__ == "__main__":
    main()
