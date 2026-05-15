from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .collector import CollectionSkipped, collect_account_files
from .config import resolve_path
from .data_api import DataApiClient
from .excel_store import ExcelStore
from .leaderboard_scanner import scan_candidates
from .models import AccountCandidate
from .notifier import format_alert_batch, format_candidate_message, send_serverchan
from .prefilter import prefilter_account
from .progress import ProgressReporter
from .scorer import score_account
from .scoring_features import write_leaderboard_context
from .state_store import StateStore


CURRENT_ALERT_REQUIRED_MARKERS = [
    "累计收益：||总PnL:",
    "账号已运行：||账号年龄天数:",
    "收益曲线平滑度：||PnL平滑调整:",
    "长期活跃表现：||长期活跃调整:",
]


TRANSIENT_DATA_API_ERROR_MARKERS = [
    "data-api.polymarket.com",
    "request failed after",
    "unexpected_eof",
    "timed out",
    "timeout",
    "http error 429",
    "too many requests",
    "connection reset",
]


def _is_transient_data_api_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "data-api.polymarket.com" in text and any(marker in text for marker in TRANSIENT_DATA_API_ERROR_MARKERS[1:])


def make_client(config: dict[str, Any]) -> DataApiClient:
    scan_cfg = config.get("scan", {}) or {}
    api_cfg = config.get("api", {}) or {}
    return DataApiClient(
        base_url=str(api_cfg.get("base_url", "https://data-api.polymarket.com")),
        timeout_seconds=int(api_cfg.get("timeout_seconds", 30)),
        max_retries=int(api_cfg.get("max_retries", 3)),
        sleep_seconds=float(scan_cfg.get("sleep_seconds", 0.2)),
    )


def candidate_from_row(row: dict[str, Any]) -> AccountCandidate:
    context = json.loads(row.get("leaderboard_context") or "{}")
    source_keys = json.loads(row.get("source_keys") or "[]")
    return AccountCandidate(
        address=row["address"],
        display_name=row.get("display_name") or row["address"],
        best_rank=row.get("best_rank"),
        discovery_score=float(row.get("discovery_score") or 0.0),
        source_keys=source_keys,
        leaderboard_context=context,
    )


def result_row(result_payload: dict[str, Any]) -> dict[str, Any]:
    review = result_payload.get("agent_review") or {}
    return {
        "generated_at_utc": result_payload.get("generated_at_utc"),
        "account_address": result_payload.get("account_address"),
        "account_label": result_payload.get("account_label"),
        "final_score": result_payload.get("final_score"),
        "decision": result_payload.get("decision"),
        "alert_grade": result_payload.get("alert_grade"),
        "auto_action": result_payload.get("auto_action"),
        "score_version": result_payload.get("score_version"),
        "discovery_score": result_payload.get("discovery_score"),
        "data_quality_score": result_payload.get("data_quality_score"),
        "pnl_quality_score": result_payload.get("pnl_quality_score"),
        "copy_capacity_score": result_payload.get("copy_capacity_score"),
        "account_total_pnl": (result_payload.get("score_breakdown_v3") or {}).get("account_total_pnl"),
        "account_age_days": (result_payload.get("score_breakdown_v3") or {}).get("account_age_days"),
        "pnl_smoothness_adjustment": (result_payload.get("score_breakdown_v3") or {}).get("pnl_smoothness_adjustment"),
        "lifetime_activity_adjustment": (result_payload.get("score_breakdown_v3") or {}).get("lifetime_activity_adjustment"),
        "lifetime_hard_blocks": ",".join((result_payload.get("score_breakdown_v3") or {}).get("lifetime_hard_blocks") or []),
        "score_flags": ",".join(result_payload.get("score_flags") or []),
        "agent_verdict": review.get("agent_verdict"),
        "agent_confidence": review.get("confidence"),
        "agent_priority": review.get("human_review_priority"),
        "agent_copy_style": review.get("copy_style"),
        "agent_reason": review.get("main_reason"),
        "agent_error": result_payload.get("agent_review_error"),
        "seen_before": result_payload.get("seen_before"),
        "scan_prompt": result_payload.get("scan_prompt"),
        "previous_status": result_payload.get("previous_status"),
        "previous_updated_at": result_payload.get("previous_updated_at"),
    }


def maybe_run_agent_review(config: dict[str, Any], result: Any) -> dict[str, Any] | None:
    agent_cfg = config.get("agent") or {}
    if not bool(agent_cfg.get("enabled", False)):
        return None
    try:
        from agent_core.config import load_config, resolve_path as resolve_agent_path
        from agent_core.candidate_reviewer import review_analysis_file
        from agent_core.memory_store import AgentMemoryStore
        from agent_core.tools import update_excel_agent_fields

        agent_config = load_config(agent_cfg.get("config_path") or "agent_core_config.example.json")
        dry_run = bool(agent_cfg.get("dry_run", False))
        memory = None if dry_run else AgentMemoryStore(resolve_agent_path(agent_config, "memory_db"))
        try:
            review = review_analysis_file(
                result.analysis_path,
                agent_config,
                memory_store=memory,
                dry_run=dry_run,
            )
        finally:
            if memory is not None:
                memory.close()
        result.payload["agent_review"] = review
        result.payload["agent_verdict"] = review.get("agent_verdict")
        result.payload["agent_confidence"] = review.get("confidence")
        result.payload["agent_priority"] = review.get("human_review_priority")
        result.payload["agent_reason"] = review.get("main_reason")
        review_path = Path(result.analysis_path).with_name("agent_review.json")
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
        result.payload["agent_review_path"] = str(review_path)
        if bool((agent_config.get("review") or {}).get("write_excel", True)):
            update_excel_agent_fields(resolve_path(config, "excel_path"), result.payload, review)
        return review
    except Exception as exc:
        result.payload["agent_review_error"] = str(exc)
        if bool(agent_cfg.get("fail_open", True)):
            return None
        raise


def _serverchan_batch_size(config: dict[str, Any]) -> int:
    serverchan_cfg = config.get("serverchan") or {}
    try:
        return max(1, int(serverchan_cfg.get("batch_size", 10)))
    except (TypeError, ValueError):
        return 10


def _serverchan_required_markers(config: dict[str, Any]) -> list[str]:
    serverchan_cfg = config.get("serverchan") or {}
    value = serverchan_cfg.get("required_message_markers", CURRENT_ALERT_REQUIRED_MARKERS)
    if value is False or value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    return list(CURRENT_ALERT_REQUIRED_MARKERS)


def _alert_threshold(config: dict[str, Any]) -> float:
    try:
        return float((config.get("scoring") or {}).get("alert_threshold", 50))
    except (TypeError, ValueError):
        return 50.0


def _new_alert_push_status(config: dict[str, Any], dry_run_alerts: bool) -> str:
    serverchan_cfg = config.get("serverchan") or {}
    if not bool(serverchan_cfg.get("enabled", True)):
        return "disabled"
    if dry_run_alerts or bool(serverchan_cfg.get("dry_run", False)):
        return "dry_run"
    return "pending"


def maybe_send_alert_batches(
    store: StateStore,
    config: dict[str, Any],
    dry_run_alerts: bool = False,
    reporter: ProgressReporter | None = None,
    cycle_id: int | None = None,
    stats: dict[str, Any] | None = None,
) -> dict[str, Any]:
    serverchan_cfg = dict(config.get("serverchan") or {})
    batch_size = _serverchan_batch_size(config)
    if not bool(serverchan_cfg.get("enabled", True)):
        return {"sent_batches": 0, "pending": 0, "batch_size": batch_size, "reason": "disabled"}
    if dry_run_alerts or bool(serverchan_cfg.get("dry_run", False)):
        return {"sent_batches": 0, "pending": 0, "batch_size": batch_size, "reason": "dry_run"}

    required_markers = _serverchan_required_markers(config)
    archived = store.archive_pending_alerts_missing_markers(required_markers, "archived_legacy_alert_schema")
    if archived:
        print(
            "[serverchan_archive] "
            + json.dumps(
                {
                    "archived": archived,
                    "reason": "archived_legacy_alert_schema",
                    "required_markers": required_markers,
                    "pending": store.pending_alert_push_count(),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    alert_threshold = _alert_threshold(config)
    archived_low_score = store.archive_pending_alerts_at_or_below_score(alert_threshold, "archived_below_alert_threshold")
    if archived_low_score:
        print(
            "[serverchan_archive] "
            + json.dumps(
                {
                    "archived": archived_low_score,
                    "reason": "archived_below_alert_threshold",
                    "alert_threshold": alert_threshold,
                    "pending": store.pending_alert_push_count(),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )

    sent_batches = 0
    last_result: dict[str, Any] | None = None
    while True:
        pending = store.pending_alerts_for_push(batch_size)
        pending_count = len(pending)
        if pending_count < batch_size:
            return {
                "sent_batches": sent_batches,
                "pending": pending_count,
                "batch_size": batch_size,
                "last_result": last_result,
            }

        if reporter is not None:
            reporter.update(
                "alerting",
                f"待推送候选已满 {batch_size} 个，正在发送 ServerChan 批量提醒",
                cycle_id=cycle_id,
                stats=stats or {},
                alert_batch_size=batch_size,
                pending_alerts=pending_count,
            )
        title, message = format_alert_batch(pending)
        alert_ids = [int(row["id"]) for row in pending]
        batch_id = f"{int(time.time())}-{alert_ids[0]}-{alert_ids[-1]}"
        send_result = send_serverchan(title, message, serverchan_cfg)
        store.mark_alert_push_result(alert_ids, batch_id, send_result)
        last_result = send_result
        print(
            "[serverchan_batch] "
            + json.dumps(
                {
                    "sent": send_result.get("sent"),
                    "reason": send_result.get("reason"),
                    "status_code": send_result.get("status_code"),
                    "serverchan_code": send_result.get("serverchan_code"),
                    "serverchan_error": send_result.get("serverchan_error"),
                    "batch_id": batch_id,
                    "batch_size": len(alert_ids),
                },
                ensure_ascii=False,
            ),
            flush=True,
        )
        if not bool(send_result.get("sent")):
            return {
                "sent_batches": sent_batches,
                "pending": store.pending_alert_push_count(),
                "batch_size": batch_size,
                "last_result": last_result,
            }
        sent_batches += 1


def run_once(
    config: dict[str, Any],
    limit_candidates: int | None = None,
    process_limit: int | None = None,
    dry_run_alerts: bool = False,
    prefilter_only: bool = False,
    client: DataApiClient | None = None,
    reporter: ProgressReporter | None = None,
) -> dict[str, Any]:
    data_dir = resolve_path(config, "data_dir")
    data_dir.mkdir(parents=True, exist_ok=True)
    store = StateStore(resolve_path(config, "state_db"))
    excel = ExcelStore(resolve_path(config, "excel_path"))
    client = client or make_client(config)
    reporter = reporter or ProgressReporter.from_config(config)
    cycle_id = store.start_cycle()
    stats = {"cycle_id": cycle_id, "scanned": 0, "processed": 0, "alerts": 0, "skipped": 0, "refresh_score": 0}
    try:
        reporter.update("cycle_started", "开始新一轮扫描", cycle_id=cycle_id, stats=stats)
        maybe_send_alert_batches(
            store,
            config,
            dry_run_alerts=dry_run_alerts,
            reporter=reporter,
            cycle_id=cycle_id,
            stats=stats,
        )
        reporter.update("scanning_leaderboard", "正在按排行榜分片发现候选账号", cycle_id=cycle_id, stats=stats)
        def report_leaderboard_progress(info: dict[str, Any]) -> None:
            message = (
                f"{info.get('shard')} offset {info.get('offset')}，"
                f"新增 {info.get('new_candidates', 0)}，累计 {info.get('unique_candidates')} 个候选"
            )
            if info.get("early_stop"):
                message += f"，提前结束分片：{info.get('early_stop_reason')}"
            reporter.update(
                "scanning_leaderboard",
                message,
                cycle_id=cycle_id,
                leaderboard=info,
                stats=stats,
            )

        candidates = scan_candidates(config, client, limit=limit_candidates, progress_callback=report_leaderboard_progress)
        stats["scanned"] = len(candidates)
        reporter.update(
            "leaderboard_scanned",
            f"发现 {len(candidates)} 个候选账号",
            cycle_id=cycle_id,
            scanned=len(candidates),
            stats=stats,
        )
        reporter.update(
            "saving_candidates",
            f"正在写入 {len(candidates)} 个候选账号到本地状态库",
            cycle_id=cycle_id,
            scanned=len(candidates),
            stats=stats,
        )
        candidate_write_summary = store.upsert_candidates(candidates, "pending")
        stats["refresh_score"] = int(candidate_write_summary.get("refresh_score") or 0)
        if stats["refresh_score"]:
            reporter.update(
                "saving_candidates",
                f"发现 {stats['refresh_score']} 个曾出现地址，已标记为“刷新分数”",
                cycle_id=cycle_id,
                scanned=len(candidates),
                candidate_write_summary=candidate_write_summary,
                stats=stats,
            )

        scan_cfg = config.get("scan") or {}
        batch_size = max(1, int(scan_cfg.get("process_batch_size", 25)))
        process_all = bool(scan_cfg.get("process_all_candidates_per_cycle", False)) and process_limit is None
        max_attempts = None if process_all else (process_limit or batch_size)
        cycle_target_total = store.pending_candidate_count()
        if max_attempts is not None:
            cycle_target_total = min(cycle_target_total, max_attempts)

        attempted = 0
        consecutive_transient_api_errors = 0
        api_error_cooldown_threshold = max(0, int(scan_cfg.get("api_error_cooldown_threshold", 3)))
        api_error_cooldown_seconds = max(0.0, float(scan_cfg.get("api_error_cooldown_seconds", 120)))
        if cycle_target_total <= 0:
            reporter.update(
                "processing_batch",
                "没有待分析账号",
                cycle_id=cycle_id,
                batch_total=0,
                stats=stats,
            )

        while True:
            remaining = None if max_attempts is None else max_attempts - attempted
            if remaining is not None and remaining <= 0:
                break
            fetch_limit = batch_size if remaining is None else min(batch_size, remaining)
            pending_rows = store.pending_candidates(fetch_limit)
            if not pending_rows:
                break

            start_index = attempted + 1
            end_index = attempted + len(pending_rows)
            reporter.update(
                "processing_batch",
                f"准备处理第 {start_index}-{end_index} / {cycle_target_total} 个待分析账号",
                cycle_id=cycle_id,
                batch_total=cycle_target_total,
                stats=stats,
            )

            for row in pending_rows:
                attempted += 1
                index = attempted
                candidate = candidate_from_row(row)
                scan_prompt = str(candidate.leaderboard_context.get("scan_prompt") or "")
                seen_before = bool(candidate.leaderboard_context.get("seen_before"))
                current_label = candidate.display_name
                if seen_before and scan_prompt:
                    current_label = f"{current_label} · {scan_prompt}" if current_label else scan_prompt
                prefilter_message = "正在做浅层交易活跃度预筛"
                if seen_before and scan_prompt:
                    prefilter_message += f"（{scan_prompt}）"
                reporter.update(
                    "prefiltering",
                    prefilter_message,
                    cycle_id=cycle_id,
                    current_account=candidate.address,
                    current_label=current_label,
                    current_index=index,
                    batch_total=cycle_target_total,
                    seen_before=seen_before,
                    scan_prompt=scan_prompt,
                    stats=stats,
                )
                prefilter = prefilter_account(candidate, client, config)
                store.record_prefilter(prefilter)
                if not prefilter.passed:
                    stats["skipped"] += 1
                    store.set_candidate_status(candidate.address, "skipped")
                    excel.append("skipped", {"account_address": candidate.address, "reason": prefilter.reason, "flags": ",".join(prefilter.flags)})
                    reporter.update(
                        "prefilter_skipped",
                        f"预筛跳过：{prefilter.reason}",
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                    continue
                if prefilter_only:
                    store.set_candidate_status(candidate.address, "prefilter_passed")
                    stats["processed"] += 1
                    reporter.update(
                        "prefilter_passed",
                        "预筛通过，已按预筛模式结束该账号",
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                    continue

                account_dir = data_dir / "accounts" / candidate.address
                context_path = write_leaderboard_context(account_dir / "leaderboard_context.json", candidate, prefilter)
                try:
                    reporter.update(
                        "collecting_account",
                        "正在拉取完整交易、持仓和 PnL 数据",
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                    csv_path, summary_path = collect_account_files(candidate.address, candidate.display_name, config, data_dir)
                    reporter.update(
                        "scoring_account",
                        "正在计算评分和跟单适配结论",
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                    result = score_account(candidate.address, csv_path, summary_path, context_path, account_dir, config)
                    consecutive_transient_api_errors = 0
                except CollectionSkipped as exc:
                    consecutive_transient_api_errors = 0
                    stats["skipped"] += 1
                    store.set_candidate_status(candidate.address, "skipped")
                    excel.append("skipped", {"account_address": candidate.address, "reason": str(exc), "flags": "hft_suspected"})
                    reporter.update(
                        "prefilter_skipped",
                        str(exc),
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                    continue
                except Exception as exc:
                    transient_api_error = _is_transient_data_api_error(exc)
                    if transient_api_error:
                        consecutive_transient_api_errors += 1
                    else:
                        consecutive_transient_api_errors = 0
                    stats["skipped"] += 1
                    reason = f"account_collection_or_scoring_failed: {exc}"
                    store.set_candidate_status(candidate.address, "defer_recheck")
                    store.record_account_error(
                        candidate.address,
                        "account_failed",
                        reason,
                        {"error": str(exc), "stage": "collect_or_score", "defer_recheck": True},
                    )
                    excel.append(
                        "skipped",
                        {
                            "account_address": candidate.address,
                            "reason": reason,
                            "flags": "account_error,defer_recheck",
                        },
                    )
                    reporter.update(
                        "account_failed",
                        "账号采集/打分失败，已延后重试：" + str(exc).splitlines()[0],
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                        error=str(exc),
                    )
                    if (
                        transient_api_error
                        and api_error_cooldown_threshold > 0
                        and consecutive_transient_api_errors >= api_error_cooldown_threshold
                        and api_error_cooldown_seconds > 0
                    ):
                        reporter.update(
                            "api_cooldown",
                            f"连续 {consecutive_transient_api_errors} 个 Polymarket API 传输异常，冷却 {int(api_error_cooldown_seconds)} 秒后继续",
                            cycle_id=cycle_id,
                            current_account=candidate.address,
                            current_label=current_label,
                            current_index=index,
                            batch_total=cycle_target_total,
                            stats=stats,
                            error=str(exc),
                            sleep_seconds=api_error_cooldown_seconds,
                        )
                        time.sleep(api_error_cooldown_seconds)
                        consecutive_transient_api_errors = 0
                    continue

                if bool((config.get("agent") or {}).get("enabled", False)):
                    reporter.update(
                        "reviewing_agent",
                        "正在执行 Agent 复核",
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                maybe_run_agent_review(config, result)
                store.record_scoring(result)
                store.set_candidate_status(candidate.address, result.auto_action)
                excel.append("all_scored", result_row(result.payload))
                stats["processed"] += 1

                if result.alert_grade in {"A", "B", "C"} and result.final_score > _alert_threshold(config):
                    reporter.update(
                        "alerting",
                        f"命中推送阈值：{result.alert_grade} / {result.final_score}",
                        cycle_id=cycle_id,
                        current_account=candidate.address,
                        current_label=current_label,
                        current_index=index,
                        batch_total=cycle_target_total,
                        stats=stats,
                    )
                    title, message = format_candidate_message(result.payload)
                    push_status = _new_alert_push_status(config, dry_run_alerts)
                    alert_id = store.record_alert(
                        candidate.address,
                        result.final_score,
                        result.alert_grade,
                        title,
                        message,
                        push_status=push_status,
                    )
                    excel.append("alerts", result_row(result.payload))
                    stats["alerts"] += 1
                    pending_count = store.pending_alert_push_count()
                    print(
                        "[serverchan_queue] "
                        + json.dumps(
                            {
                                "alert_id": alert_id,
                                "push_status": push_status,
                                "pending": pending_count,
                                "batch_size": _serverchan_batch_size(config),
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    maybe_send_alert_batches(
                        store,
                        config,
                        dry_run_alerts=dry_run_alerts,
                        reporter=reporter,
                        cycle_id=cycle_id,
                        stats=stats,
                    )
                reporter.update(
                    "account_done",
                    f"账号处理完成：{result.auto_action}",
                    cycle_id=cycle_id,
                    current_account=candidate.address,
                    current_label=current_label,
                    current_index=index,
                    batch_total=cycle_target_total,
                    final_score=result.final_score,
                    alert_grade=result.alert_grade,
                    auto_action=result.auto_action,
                    stats=stats,
                )

        excel.append("cycles", {"cycle_id": cycle_id, **stats})
        store.finish_cycle(cycle_id, "done", json.dumps(stats, ensure_ascii=False))
        reporter.update("cycle_done", "本轮扫描完成", cycle_id=cycle_id, stats=stats)
        return stats
    except Exception as exc:
        store.finish_cycle(cycle_id, "failed", str(exc))
        reporter.update("cycle_failed", str(exc), cycle_id=cycle_id, stats=stats, error=str(exc))
        raise
    finally:
        store.close()


def run_forever(config: dict[str, Any], dry_run_alerts: bool = False) -> None:
    scan_cfg = config.get("scan") or {}
    sleep_seconds = float(scan_cfg.get("cycle_sleep_seconds", 600))
    failure_sleep_seconds = float(scan_cfg.get("failure_sleep_seconds", min(60.0, sleep_seconds)))
    reporter = ProgressReporter.from_config(config)
    while True:
        try:
            stats = run_once(config, dry_run_alerts=dry_run_alerts, reporter=reporter)
            sleep_for = max(1.0, sleep_seconds)
            reporter.update(
                "sleeping",
                f"本轮完成，休眠 {int(sleep_for)} 秒后继续",
                cycle_id=stats.get("cycle_id"),
                sleep_seconds=sleep_for,
                stats=stats,
            )
        except Exception as exc:
            sleep_for = max(1.0, failure_sleep_seconds)
            reporter.update(
                "sleeping",
                f"本轮失败，休眠 {int(sleep_for)} 秒后重试：{str(exc).splitlines()[0]}",
                sleep_seconds=sleep_for,
                stats={},
                error=str(exc),
            )
        time.sleep(sleep_for)
