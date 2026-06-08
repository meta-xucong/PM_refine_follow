let state = {};
let configs = {};
let processRefreshInFlight = false;
let fullRefreshInFlight = false;
let lastFullRefreshAt = 0;

const PROCESS_REFRESH_MS = 10000;
const FULL_REFRESH_MS = 60000;

const $ = (id) => document.getElementById(id);

function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 2600);
}

function setRefreshStatus(text, className = "") {
  const el = $("refreshStatus");
  if (!el) return;
  el.textContent = text;
  el.className = `refresh-status ${className}`.trim();
}

function refreshTimeText() {
  return new Date().toLocaleTimeString("zh-CN", { hour12: false });
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json();
  if (!res.ok || data.error) throw new Error(data.error || res.statusText);
  return data;
}

function setBadge(process) {
  const badge = $("processBadge");
  if (process.running) {
    badge.textContent = `运行中 PID ${process.pid}`;
    badge.className = "badge running";
  } else {
    badge.textContent = "未运行";
    badge.className = "badge stopped";
  }
}

function fmt(v) {
  if (v === null || v === undefined || v === "") return "-";
  if (typeof v === "number") return Number.isInteger(v) ? String(v) : v.toFixed(2);
  return String(v);
}

function html(v) {
  return fmt(v).replace(/[&<>"']/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[ch]));
}

function shortAddress(address) {
  if (!address) return "-";
  return address.length > 14 ? `${address.slice(0, 8)}...${address.slice(-6)}` : address;
}

function copyButton(value, label = "复制地址") {
  const safeValue = html(value);
  return `
    <button type="button" class="copy-btn" data-copy="${safeValue}" title="${html(label)}" aria-label="${html(label)}">
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <rect x="9" y="9" width="10" height="10" rx="2"></rect>
        <path d="M5 15V7a2 2 0 0 1 2-2h8"></path>
      </svg>
    </button>
  `;
}

async function copyText(value) {
  const text = fmt(value);
  if (!text || text === "-") return;
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch (_) {
      // Fall back to a temporary textarea when browser permissions block clipboard access.
    }
  }
  const input = document.createElement("textarea");
  input.value = text;
  input.setAttribute("readonly", "");
  input.style.position = "fixed";
  input.style.left = "-9999px";
  document.body.appendChild(input);
  input.select();
  document.execCommand("copy");
  input.remove();
}

function ageText(seconds) {
  if (seconds === null || seconds === undefined) return "-";
  if (seconds < 60) return `${Math.round(seconds)} 秒前`;
  if (seconds < 3600) return `${Math.round(seconds / 60)} 分钟前`;
  return `${(seconds / 3600).toFixed(1)} 小时前`;
}

function fmtTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return fmt(value);
  return date.toLocaleString("zh-CN", { hour12: false });
}

function leaderboardStopText(reason) {
  const mapping = {
    api_rank_cap: "官方接口已到可见末尾",
    no_new_candidates: "连续多页没有新增账号",
    empty_page: "接口返回空页",
  };
  return mapping[reason] || reason || "";
}

function storedCandidateText(progress) {
  return `当前数据库已保存 ${fmt(progress.candidate_total_count)} 个地址；扫榜完成后会把本轮候选批量写入`;
}

function renderStatus(data) {
  state = data;
  setBadge(data.process || {});
  renderProgress(data.progress || {}, data.process || {});
  const counts = data.auto?.candidate_counts || {};
  const totalCount = data.auto?.candidate_total_count ?? Object.values(counts).reduce((sum, value) => sum + Number(value || 0), 0);
  const alertPushCounts = data.auto?.alert_push_counts || {};
  const statusText = Object.entries(counts).map(([k, v]) => `${k}:${v}`).join("  ");
  $("candidateCounts").textContent = `总地址:${fmt(totalCount)}${statusText ? `  ${statusText}` : ""}`;
  $("alertCount").textContent = `${fmt((data.excel?.sheet_counts || {}).alerts || 0)} / 待推送:${fmt(alertPushCounts.pending || 0)}`;
  $("agentCount").textContent = fmt((data.agent?.counts || {}).agent_decisions || 0);

  renderCycles(data.auto?.latest_cycles || []);
  renderRuns(data.auto?.recent_runs || []);
  renderAlerts(data.excel?.alerts || data.auto?.recent_alerts || []);
  renderAgentReviews(data.excel?.agent_reviews || []);
  renderPushedAccounts(data.auto?.pushed_accounts || []);
}

function renderProgress(progress, process) {
  const health = progress.health || (process.running ? "starting" : "stopped");
  const leaderboard = progress.leaderboard || null;
  const candidateSource = progress.candidate_source || null;
  const leaderboardScan = progress.leaderboard_scan || {};
  $("statusDot").className = `status-dot ${health}`;
  $("currentPhase").textContent = progress.phase_label || (process.running ? "运行中" : "未运行");
  $("currentMessage").textContent = progress.message || "-";
  $("currentCycle").textContent = `Cycle ${fmt(progress.cycle_id)}`;
  $("heartbeatAge").textContent = progress.updated_at ? `心跳 ${ageText(progress.age_seconds)}` : "暂无心跳";

  if (progress.current_account) {
    const labelText = progress.current_label || "正在处理该地址";
    const scanPrompt = progress.scan_prompt && !labelText.includes(progress.scan_prompt) ? ` · ${progress.scan_prompt}` : "";
    $("currentTargetLarge").textContent = progress.current_account;
    $("currentTargetHint").textContent = `${labelText}${scanPrompt} · ${progress.current_index ? `批次 ${fmt(progress.current_index)} / ${fmt(progress.batch_total)}` : "等待批次信息"}`;
  } else if (leaderboard) {
    $("currentTargetLarge").textContent = "正在扫描排行榜";
    $("currentTargetHint").textContent = progress.current_target_hint || "当前在发现候选地址，还没有开始处理单个地址";
  } else {
    $("currentTargetLarge").textContent = fmt(progress.current_target);
    $("currentTargetHint").textContent = progress.current_target_hint || "-";
  }

  if (leaderboard) {
    const shardIndex = leaderboard.total_shards ? `${fmt(leaderboard.shard_index)} / ${fmt(leaderboard.total_shards)}` : "-";
    const offsetEnd = Number(leaderboard.offset || 0) + Number(leaderboard.page_limit || 0);
    const noNew = leaderboard.no_new_pages ? `，连续无新增 ${fmt(leaderboard.no_new_pages)} 页` : "";
    const rankRange = leaderboard.first_rank ? `，返回排名 ${fmt(leaderboard.first_rank)}-${fmt(leaderboard.last_rank)}` : "";
    const cap = leaderboard.api_cap_detected ? `，官方可见上限约 ${fmt(leaderboard.api_cap_rank)} 名` : "";
    const earlyStop = leaderboard.early_stop ? `，提前结束：${leaderboardStopText(leaderboard.early_stop_reason)}` : "";
    const storedTotal = progress.candidate_total_count !== undefined ? `；${storedCandidateText(progress)}` : "";
    $("leaderboardProgress").textContent = `${fmt(leaderboard.shard)} (${shardIndex})`;
    $("leaderboardHint").textContent = `offset ${fmt(leaderboard.offset)}-${fmt(offsetEnd)} / ${fmt(leaderboard.max_rank)}${rankRange}，本页新增 ${fmt(leaderboard.new_candidates)}，本轮候选 ${fmt(leaderboard.unique_candidates)}${storedTotal}${noNew}${cap}${earlyStop}`;
  } else {
    $("leaderboardProgress").textContent = "-";
    $("leaderboardHint").textContent = process.running ? "已离开排行榜扫榜阶段" : "-";
  }

  if (candidateSource) {
    const marketText = candidateSource.market_slug ? ` · ${fmt(candidateSource.market_slug)}` : "";
    const indexText = candidateSource.total_markets ? ` (${fmt(candidateSource.market_index)} / ${fmt(candidateSource.total_markets)})` : "";
    const storedTotal = progress.candidate_total_count !== undefined ? `；${storedCandidateText(progress)}` : "";
    $("leaderboardProgress").textContent = `${fmt(candidateSource.source)}${indexText}`;
    $("leaderboardHint").textContent = `官方信源${marketText}，返回 ${fmt(candidateSource.rows || candidateSource.markets || 0)} 条，新增 ${fmt(candidateSource.new_candidates || 0)}，本轮候选 ${fmt(candidateSource.unique_candidates || 0)}${storedTotal}`;
  }

  const requestedCap = leaderboardScan.requested_rank_cap || leaderboard?.max_rank;
  const visibleCap = leaderboardScan.api_visible_cap_rank || leaderboard?.api_cap_rank;
  const uniqueCandidates = leaderboardScan.unique_candidates || leaderboard?.unique_candidates;
  const capDetected = Boolean(leaderboardScan.api_cap_detected || leaderboard?.api_cap_detected);
  if (capDetected) {
    $("leaderboardCap").textContent = `约 ${fmt(visibleCap)} 名`;
    $("leaderboardCapHint").textContent = `目标 ${fmt(requestedCap)} 名；官方接口已触顶，本轮多榜合并候选 ${fmt(uniqueCandidates)} 个；${storedCandidateText(progress)}`;
  } else if (requestedCap) {
    $("leaderboardCap").textContent = `目标 ${fmt(requestedCap)} 名`;
    $("leaderboardCapHint").textContent = uniqueCandidates ? `本轮已发现 ${fmt(uniqueCandidates)} 个候选；${storedCandidateText(progress)}；尚未检测到接口触顶` : `等待扫榜进度；${storedCandidateText(progress)}`;
  } else {
    $("leaderboardCap").textContent = "-";
    $("leaderboardCapHint").textContent = process.running ? "等待扫榜进度" : "-";
  }

  $("nextStep").textContent = progress.next_step || "-";
  $("nextStepHint").textContent = progress.updated_at ? `最近心跳 ${ageText(progress.age_seconds)}` : "暂无心跳";

  if (progress.current_account) {
    $("currentAccount").textContent = `${progress.current_account} ${progress.current_label ? `(${progress.current_label})` : ""}`;
  } else if (leaderboard) {
    $("currentAccount").textContent = "扫榜阶段：尚无单个地址";
  } else {
    $("currentAccount").textContent = "-";
  }
  if (progress.batch_total) {
    $("batchProgress").textContent = `${fmt(progress.current_index)} / ${fmt(progress.batch_total)} (${fmt(progress.percent)}%)`;
  } else if (leaderboard && progress.percent !== null && progress.percent !== undefined) {
    $("batchProgress").textContent = `扫榜 ${fmt(progress.percent)}%`;
  } else {
    $("batchProgress").textContent = progress.percent === 100 ? "100%" : "-";
  }
  const stats = progress.stats || {};
  $("cycleStats").textContent = `扫:${fmt(stats.scanned)} 处理:${fmt(stats.processed)} 推送:${fmt(stats.alerts)} 跳过:${fmt(stats.skipped)}`;
  $("lastAction").textContent = progress.auto_action || progress.alert_grade || (leaderboard ? `本轮候选 ${fmt(leaderboard.unique_candidates)} / 数据库已保存 ${fmt(progress.candidate_total_count)}` : (progress.phase || "-"));
  $("progressFill").style.width = `${Number(progress.percent || 0)}%`;
  renderTimeline(progress.history || []);
}

function renderTimeline(rows) {
  $("timelineHint").textContent = rows.length ? `${rows.length} 条，5 秒自动刷新` : "暂无事件";
  $("progressTimeline").innerHTML = rows.map((r) => {
    const leaderboard = r.leaderboard || null;
    const detail = r.current_account
      ? `${shortAddress(r.current_account)}${r.current_label ? ` · ${r.current_label}` : ""}`
      : (leaderboard ? `${fmt(leaderboard.shard)} offset ${fmt(leaderboard.offset)}` : (r.candidate_source ? `${fmt(r.candidate_source.source)} ${fmt(r.candidate_source.market_slug || "")}` : ""));
    const when = r.updated_ts ? ageText(Math.max(0, (Date.now() / 1000) - Number(r.updated_ts))) : "-";
    return `
      <div class="timeline-item">
        <div class="timeline-phase">${html(r.phase_label || r.phase)}</div>
        <div class="timeline-message">${html(r.message || "")}</div>
        <div class="timeline-account" title="${html(detail)}">${html(detail || when)}</div>
      </div>
    `;
  }).join("") || `<div class="timeline-item"><div class="timeline-phase">暂无</div><div class="timeline-message">还没有收到进度心跳</div><div class="timeline-account">-</div></div>`;
}

function renderCycles(rows) {
  $("cyclesBody").innerHTML = rows.map((r) => `
    <tr>
      <td>${html(r.id)}</td>
      <td>${html(r.status)}</td>
      <td title="${html(r.started_at)}">${html(fmtTime(r.started_at))}</td>
      <td title="${html(r.finished_at)}">${html(fmtTime(r.finished_at))}</td>
      <td>${html(r.note)}</td>
    </tr>
  `).join("") || `<tr><td colspan="5">暂无周期</td></tr>`;
}

function renderRuns(rows) {
  $("runsBody").innerHTML = rows.map((r) => `
    <tr>
      <td title="${html(r.address)}">${html(shortAddress(r.address))}</td>
      <td>${html(r.status)}</td>
      <td>${html(r.final_score)}</td>
      <td>${html(r.alert_grade)}</td>
      <td title="${html(r.created_at)}">${html(fmtTime(r.created_at))}</td>
    </tr>
  `).join("") || `<tr><td colspan="5">暂无任务</td></tr>`;
}

function renderAccounts(rows) {
  $("accountsBody").innerHTML = rows.map((r) => `
    <tr>
      <td class="account-cell" title="${html(r.address)}">
        ${r.label && r.label !== r.address ? `<div class="account-label">${html(r.label)}</div>` : ""}
        <div class="address-row">
          <span class="address-full">${html(r.address)}</span>
          ${copyButton(r.address)}
        </div>
      </td>
      <td>${html(r.final_score)}</td>
      <td>${html(r.alert_grade)}</td>
      <td>${html(r.auto_action)}${r.scan_prompt ? `<br><span class="muted">${html(r.scan_prompt)}</span>` : ""}</td>
      <td>${html(r.agent_verdict)}<br><span class="muted">${html(r.agent_confidence)}</span></td>
      <td>${html(r.data_quality_score)}</td>
      <td>${html(r.pnl_quality_score)}</td>
      <td>${html(r.copy_capacity_score)}</td>
      <td>${renderScoreHistory(r.score_history || [])}</td>
      <td>${html(r.updated_at)}</td>
    </tr>
  `).join("") || `<tr><td colspan="10">暂无候选</td></tr>`;
}

function renderScoreHistory(rounds) {
  if (!rounds.length) return "-";
  return `
    <div class="score-stack compact">
      ${rounds.slice(0, 4).map((round, index) => `
        <span class="score-pill" title="${html(fmtTime(round.created_at))}｜${html(round.action)}">
          ${index === 0 ? "最新" : `旧${index}`}：${html(round.score)} ${html(round.grade)}
        </span>
      `).join("")}
    </div>
  `;
}

function renderAlerts(rows) {
  $("alertsList").innerHTML = rows.map((r) => `
    <div class="list-item">
      <div class="line1"><span>${html(r.account_label || r.account_address || r.address)}</span><span>${html(r.alert_grade)} ${html(r.final_score)}</span></div>
      <div class="meta">${html([r.auto_action || r.title || "", r.push_status ? `推送状态: ${r.push_status}` : "", r.score_flags || r.message || ""].filter(Boolean).join("\n"))}</div>
    </div>
  `).join("") || `<div class="list-item">暂无告警</div>`;
}

function renderRoundChip(round) {
  return `
    <span class="score-pill" title="批次：${html(round.batch_id)}｜时间：${html(fmtTime(round.pushed_at))}">
      第 ${html(round.round_number)} 轮：${html(round.score)} 分 ${html(round.grade)}
    </span>
  `;
}

function renderPushedAccounts(rows) {
  const totalRounds = rows.reduce((sum, row) => sum + Number(row.push_count || 0), 0);
  $("pushedHistoryHint").textContent = rows.length ? `${rows.length} 个账号，累计 ${totalRounds} 次推送，5 秒自动更新` : "暂无已推送账号";
  $("pushedHistoryBody").innerHTML = rows.map((r) => {
    const recent = r.recent_rounds || [];
    const hidden = r.hidden_rounds || [];
    return `
      <tr>
        <td class="account-cell" title="${html(r.address)}">
          ${r.label && r.label !== r.address ? `<div class="account-label">${html(r.label)}</div>` : ""}
          <div class="address-row">
            <span class="address-full">${html(r.address)}</span>
            ${copyButton(r.address)}
          </div>
        </td>
        <td>${html(r.push_count)} 轮</td>
        <td><div class="score-stack">${recent.map(renderRoundChip).join("") || "-"}</div></td>
        <td>
          ${hidden.length ? `
            <details class="history-details">
              <summary>查看剩余 ${hidden.length} 轮</summary>
              <div class="score-stack">${hidden.map(renderRoundChip).join("")}</div>
            </details>
          ` : "-"}
        </td>
        <td title="${html(r.latest_pushed_at)}">${html(fmtTime(r.latest_pushed_at))}</td>
      </tr>
    `;
  }).join("") || `<tr><td colspan="5">暂无已推送账号</td></tr>`;
}

function recommendationText(value) {
  const mapping = {
    stable: "稳定",
    watch: "观察",
    downgrade: "降级",
    remove_candidate: "移出",
    error: "失败",
  };
  return mapping[value] || value || "-";
}

function recommendationClass(value) {
  return `recommendation-pill rec-${String(value || "unknown").replace(/[^a-z0-9_-]/gi, "_")}`;
}

function renderFlagStack(flags, caps) {
  const values = [...(flags || []), ...(caps || [])].filter(Boolean).slice(0, 5);
  if (!values.length) return "-";
  return `<div class="flag-stack">${values.map((value) => `<span class="flag-chip">${html(value)}</span>`).join("")}</div>`;
}

function renderScoreDelta(value) {
  if (value === null || value === undefined || value === "") return "-";
  const n = Number(value);
  const className = n > 0 ? "delta-up" : (n < 0 ? "delta-down" : "delta-flat");
  const text = Number.isNaN(n) ? fmt(value) : `${n > 0 ? "+" : ""}${n.toFixed(2)}`;
  return `<span class="${className}">${html(text)}</span>`;
}

function renderWatchlistScoreChip(run, index) {
  const recommendation = run.recommendation || (run.error ? "error" : "");
  const label = index === 0 ? "最新" : `旧${index}`;
  const title = [
    `批次 ${fmt(run.batch_id)}`,
    fmtTime(run.created_at),
    `旧分 ${fmt(run.old_score)}`,
    `fresh ${fmt(run.fresh_score)}`,
    recommendationText(recommendation),
  ].join("｜");
  return `
    <span class="score-pill watchlist-score-chip" title="${html(title)}">
      ${html(label)}：${html(run.fresh_score)} ${renderScoreDelta(run.score_delta)}
    </span>
  `;
}

function renderWatchlistHistory(row) {
  const recent = row.recent_history || [];
  const hidden = row.hidden_history || [];
  if (!recent.length) return "-";
  return `
    <div class="score-stack">${recent.map((run, index) => renderWatchlistScoreChip(run, index)).join("")}</div>
    ${hidden.length ? `
      <details class="history-details watchlist-history-details">
        <summary>查看剩余 ${hidden.length} 次</summary>
        <div class="score-stack">${hidden.map((run, index) => renderWatchlistScoreChip(run, index + recent.length)).join("")}</div>
      </details>
    ` : ""}
  `;
}

function renderWatchlistRefresh(data) {
  if (!$("watchlistBody")) return;
  const process = data.process || {};
  const latestBatch = data.latest_batch || {};
  const latestFile = data.latest_file || {};
  const summary = latestBatch.summary || latestFile.summary || {};
  const accountRows = (data.account_histories || []).slice(0, 120);
  const isRunning = Boolean(process.running);

  $("watchlistProcess").textContent = isRunning ? (process.pid ? `运行中 PID ${process.pid}` : "运行中") : "空闲";
  $("watchlistProcessHint").textContent = process.started_at
    ? `启动时间 ${fmtTime(process.started_at)}${process.source ? ` · ${fmt(process.source)}` : ""}`
    : (process.stale ? "上次进程已结束" : "等待定时或手动触发");

  $("watchlistBatch").textContent = latestBatch.id ? `#${fmt(latestBatch.id)} ${fmt(latestBatch.status)}` : "-";
  $("watchlistBatchHint").textContent = latestBatch.started_at
    ? `${fmtTime(latestBatch.started_at)} -> ${fmtTime(latestBatch.finished_at)}`
    : "暂无复核批次";

  $("watchlistSummary").textContent = latestBatch.id
    ? `稳 ${fmt(latestBatch.stable_count)} / 观 ${fmt(latestBatch.watch_count)} / 降 ${fmt(latestBatch.downgrade_count)} / 移 ${fmt(latestBatch.remove_count)}`
    : "-";
  $("watchlistSummaryHint").textContent = latestBatch.id
    ? `实际复核 ${fmt(summary.attempted ?? latestBatch.succeeded + latestBatch.failed)}，成功 ${fmt(latestBatch.succeeded)}，失败 ${fmt(latestBatch.failed)}，48小时跳过 ${fmt(latestBatch.skipped_recent)}`
    : "只复核最新评分或最新推送分数 >= 60 的账号";

  const pushStatus = latestBatch.serverchan_push_status || "-";
  $("watchlistPush").textContent = pushStatus === "sent" ? "已推送" : fmt(pushStatus);
  $("watchlistPushHint").textContent = latestBatch.serverchan_pushed_at
    ? `推送时间 ${fmtTime(latestBatch.serverchan_pushed_at)}`
    : "每个批次结束后发送一次汇总";

  $("watchlistHint").textContent = latestBatch.id
    ? `最近批次 ${fmtTime(latestBatch.finished_at || latestBatch.started_at)}，表格显示 ${accountRows.length} 个账号`
    : "暂无复核结果";

  $("watchlistBody").innerHTML = accountRows.map((row) => {
    const r = row.latest || {};
    const recommendation = r.recommendation || (r.error ? "error" : "-");
    return `
      <tr>
        <td class="account-cell" title="${html(r.address)}">
          ${r.label && r.label !== r.address ? `<div class="account-label">${html(r.label)}</div>` : ""}
          <div class="address-row">
            <span class="address-full">${html(r.address)}</span>
            ${copyButton(r.address)}
          </div>
        </td>
        <td>${html(r.source_reason)}</td>
        <td>${html(r.fresh_score)}</td>
        <td>${renderScoreDelta(r.score_delta)}</td>
        <td><span class="${recommendationClass(recommendation)}">${html(recommendationText(recommendation))}</span>${r.error ? `<br><span class="muted">${html(r.error)}</span>` : ""}</td>
        <td>${renderWatchlistHistory(row)}</td>
        <td>${renderFlagStack(r.score_flags, r.applied_caps)}</td>
        <td title="${html(r.created_at)}">${html(fmtTime(r.created_at))}</td>
      </tr>
    `;
  }).join("") || `<tr><td colspan="8">暂无复核记录</td></tr>`;
}

function renderServerchanKey(info) {
  if (!info) return;
  const source = info.active_source || "未设置";
  const masked = info.active_masked || "未设置";
  $("serverchanKeyStatus").textContent = `当前生效：${source}（${masked}）。${info.note || ""}`;
  $("serverchanKeyPath").textContent = `保存位置：${info.file_path || "-"}；环境变量：${info.env_name || "SCT_SENDKEY"}${info.env_present ? `（已设置 ${info.env_masked || ""}）` : "（未设置）"}`;
}

function renderAgentReviews(rows) {
  $("agentReviewsList").innerHTML = rows.map((r) => `
    <div class="list-item">
      <div class="line1"><span>${html(r.account_label || r.account_address)}</span><span>${html(r.agent_verdict)} / ${html(r.agent_confidence)}</span></div>
      <div class="meta">${html(r.agent_reason)}\n${html(r.agent_risk_summary)}</div>
    </div>
  `).join("") || `<div class="list-item">暂无 Agent 复核</div>`;
}

function loadConfigForms(cfg) {
  configs = cfg;
  const auto = cfg.auto_config || {};
  $("cfgMaxRank").value = auto.scan?.max_rank ?? 100000;
  $("cfgBatch").value = auto.scan?.process_batch_size ?? 25;
  $("cfgSleep").value = auto.scan?.cycle_sleep_seconds ?? 600;
  $("cfgNoNewPages").value = auto.scan?.leaderboard_no_new_pages_stop ?? 40;
  $("cfgAlertThreshold").value = auto.scoring?.alert_threshold ?? 50;
  $("cfgAgentEnabled").checked = Boolean(auto.agent?.enabled);
  $("cfgServerEnabled").checked = Boolean(auto.serverchan?.enabled);
  $("cfgServerBatch").value = auto.serverchan?.batch_size ?? 10;
  $("configEditor").value = JSON.stringify(cfg, null, 2);
}

function collectConfigFromForm() {
  const full = JSON.parse($("configEditor").value);
  const auto = full.auto_config || {};
  auto.scan = auto.scan || {};
  auto.scoring = auto.scoring || {};
  auto.agent = auto.agent || {};
  auto.serverchan = auto.serverchan || {};
  auto.scan.max_rank = Number($("cfgMaxRank").value || auto.scan.max_rank || 100000);
  auto.scan.process_batch_size = Number($("cfgBatch").value || auto.scan.process_batch_size || 25);
  auto.scan.cycle_sleep_seconds = Number($("cfgSleep").value || auto.scan.cycle_sleep_seconds || 600);
  auto.scan.leaderboard_no_new_pages_stop = Number($("cfgNoNewPages").value || auto.scan.leaderboard_no_new_pages_stop || 40);
  auto.scoring.alert_threshold = Number($("cfgAlertThreshold").value || auto.scoring.alert_threshold || 50);
  auto.agent.enabled = $("cfgAgentEnabled").checked;
  auto.serverchan.enabled = $("cfgServerEnabled").checked;
  auto.serverchan.batch_size = Number($("cfgServerBatch").value || auto.serverchan.batch_size || 10);
  full.auto_config = auto;
  return full;
}

async function refreshAll() {
  const [status, config, accounts, proc, sendkey, watchlist] = await Promise.all([
    api("/api/status"),
    api("/api/config"),
    api("/api/accounts?limit=80"),
    api("/api/process"),
    api("/api/serverchan-key"),
    api("/api/watchlist-refresh/status"),
  ]);
  renderStatus(status);
  renderAccounts(accounts.accounts || []);
  $("logTail").textContent = proc.log_tail || "";
  loadConfigForms(config);
  renderServerchanKey(sendkey);
  renderWatchlistRefresh(watchlist);
  lastFullRefreshAt = Date.now();
  setRefreshStatus(`已更新 ${refreshTimeText()}`);
}

async function refreshDashboardData() {
  const [status, accounts, proc, sendkey, watchlist] = await Promise.all([
    api("/api/status"),
    api("/api/accounts?limit=80"),
    api("/api/process"),
    api("/api/serverchan-key"),
    api("/api/watchlist-refresh/status"),
  ]);
  renderStatus(status);
  renderAccounts(accounts.accounts || []);
  $("logTail").textContent = proc.log_tail || "";
  renderServerchanKey(sendkey);
  renderWatchlistRefresh(watchlist);
  lastFullRefreshAt = Date.now();
  setRefreshStatus(`已更新 ${refreshTimeText()}`);
}

async function startRun() {
  const body = { dry_run_alerts: $("dryRunAlerts").checked };
  const res = await api("/api/start", { method: "POST", body: JSON.stringify(body) });
  toast(res.started ? `已启动 PID ${res.pid}` : `未启动：${res.reason}`);
  await refreshDashboardData();
}

async function runOnce() {
  const body = {
    limit_candidates: Number($("limitCandidates").value || 10),
    process_limit: Number($("processLimit").value || 3),
    dry_run_alerts: $("dryRunAlerts").checked,
    prefilter_only: $("prefilterOnly").checked,
  };
  const res = await api("/api/run-once", { method: "POST", body: JSON.stringify(body) });
  toast(res.started ? `单轮任务已启动 PID ${res.pid}` : `未启动：${res.reason}`);
  await refreshDashboardData();
}

async function stopRun() {
  const res = await api("/api/stop", { method: "POST", body: "{}" });
  toast(res.stopped ? "已停止" : `未停止：${res.reason}`);
  await refreshDashboardData();
}

async function saveConfig() {
  const full = collectConfigFromForm();
  await api("/api/config", { method: "POST", body: JSON.stringify(full) });
  toast("配置已保存");
  await refreshAll();
}

async function loadServerchanKeyStatus() {
  renderServerchanKey(await api("/api/serverchan-key"));
  toast("密钥状态已刷新");
}

async function saveServerchanKey() {
  const input = $("serverchanSendkeyInput");
  const sendkey = input.value.trim();
  if (!sendkey) {
    toast("请输入新的 SendKey");
    return;
  }
  const info = await api("/api/serverchan-key", { method: "POST", body: JSON.stringify({ sendkey }) });
  input.value = "";
  renderServerchanKey(info);
  toast("SendKey 已保存");
}

function downloadPushedCsv() {
  window.location.href = "/api/export/pushed.csv";
}

function downloadWatchlistCsv() {
  window.location.href = "/api/watchlist-refresh/export.csv";
}

async function runWatchlistRefresh() {
  const cfg = configs.auto_config?.watchlist_refresh || {};
  const body = {
    min_score: Number(cfg.min_score ?? 60),
    limit: Number(cfg.limit ?? 200),
    interval_hours: Number(cfg.interval_hours ?? 48),
    dry_run_serverchan: $("dryRunAlerts").checked,
  };
  const res = await api("/api/watchlist-refresh/run", { method: "POST", body: JSON.stringify(body) });
  toast(res.started ? `高分复核已启动 PID ${res.pid}` : `未启动：${res.reason}`);
  await refreshDashboardData();
}

async function refreshProcessOnly() {
  const [proc, watchlist] = await Promise.all([
    api("/api/process"),
    api("/api/watchlist-refresh/status"),
  ]);
  const merged = {
    process: proc.process || state.process || {},
    progress: proc.progress || state.progress || {},
    auto: proc.auto || state.auto || {},
    agent: state.agent || {},
    excel: proc.excel || state.excel || {},
  };
  renderStatus(merged);
  renderWatchlistRefresh(watchlist);
  $("logTail").textContent = proc.log_tail || "";
  setRefreshStatus(`已更新 ${refreshTimeText()}`);
}

async function autoRefreshTick() {
  if (document.hidden) return;
  if (processRefreshInFlight) return;
  processRefreshInFlight = true;
  setRefreshStatus("更新中...", "updating");
  try {
    await refreshProcessOnly();
  } catch (_) {
    setRefreshStatus("自动刷新失败", "error");
  } finally {
    processRefreshInFlight = false;
  }
}

async function autoFullRefreshTick() {
  if (document.hidden) return;
  if (fullRefreshInFlight) return;
  if (Date.now() - lastFullRefreshAt < FULL_REFRESH_MS - 500) return;
  fullRefreshInFlight = true;
  try {
    await refreshDashboardData();
  } catch (_) {
    setRefreshStatus("自动刷新失败", "error");
  } finally {
    fullRefreshInFlight = false;
  }
}

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((x) => x.classList.remove("active"));
    btn.classList.add("active");
    $(btn.dataset.tab).classList.add("active");
  });
});

$("refreshBtn").addEventListener("click", () => {
  setRefreshStatus("更新中...", "updating");
  refreshAll().catch((e) => {
    setRefreshStatus("刷新失败", "error");
    toast(e.message);
  });
});
$("startBtn").addEventListener("click", () => startRun().catch((e) => toast(e.message)));
$("runOnceBtn").addEventListener("click", () => runOnce().catch((e) => toast(e.message)));
$("stopBtn").addEventListener("click", () => stopRun().catch((e) => toast(e.message)));
$("saveConfigBtn").addEventListener("click", () => saveConfig().catch((e) => toast(e.message)));
$("refreshSendkeyBtn").addEventListener("click", () => loadServerchanKeyStatus().catch((e) => toast(e.message)));
$("saveSendkeyBtn").addEventListener("click", () => saveServerchanKey().catch((e) => toast(e.message)));
$("downloadPushedCsvBtn").addEventListener("click", downloadPushedCsv);
$("downloadExcelCsvBtn").addEventListener("click", downloadPushedCsv);
$("downloadWatchlistCsvBtn").addEventListener("click", downloadWatchlistCsv);
$("runWatchlistRefreshBtn").addEventListener("click", () => runWatchlistRefresh().catch((e) => toast(e.message)));
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-copy]");
  if (!button) return;
  copyText(button.dataset.copy).then(() => toast("已复制地址")).catch((e) => toast(`复制失败：${e.message}`));
});

refreshAll().catch((e) => {
  setRefreshStatus("刷新失败", "error");
  toast(e.message);
});
setInterval(autoRefreshTick, PROCESS_REFRESH_MS);
setInterval(autoFullRefreshTick, FULL_REFRESH_MS);
document.addEventListener("visibilitychange", () => {
  if (!document.hidden) refreshDashboardData().catch(() => {});
});
