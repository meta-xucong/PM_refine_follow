# Local Dashboard Frontend

## 1. Goal

The dashboard is a local operator console for the Polymarket account screening system. It keeps the existing CLI workflow intact, while giving non-technical users a single browser page for configuration, starting and stopping scans, viewing progress, reviewing candidates, and checking Agent decisions.

## 2. Entry Point

Start the dashboard from the repository root:

```powershell
python -m dashboard.server --host 127.0.0.1 --port 8787
```

Then open:

```text
http://127.0.0.1:8787
```

The dashboard creates two local UI config files on first launch:

- `auto_screen_config.ui.json`
- `agent_core_config.ui.json`

These are copied from the example configs and are ignored by git, so users can safely edit them locally.

## 3. User-Facing Features

- One-click single-run scan with candidate limit, processing limit, dry-run alert mode, and prefilter-only mode.
- One-click resident scan using the scheduler loop.
- Stop button for the currently launched scan process.
- Live process badge, PID, command mode, and log tail.
- Live running status panel with current phase, heartbeat age, cycle id, current target address, leaderboard shard offset, next step, batch progress, cycle counters, and recent progress event stream.
- Key metrics for candidate states, alert records, Agent decision counts, and Excel output path.
- Cycle and run history tables from the screening state database.
- Candidate table showing score, grade, action, Agent verdict, data quality, PnL quality, copy capacity, and report paths.
- Alert and Agent review views for quick inspection.
- Basic config form for high-frequency settings.
- Advanced JSON editor for full config control.

## 4. Backend API

The dashboard backend is a small stdlib HTTP server in `dashboard/server.py`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/config` | Load UI config JSON and config file paths. |
| `POST` | `/api/config` | Save `auto_config` and `agent_config`. |
| `GET` | `/api/status` | Load process, screening DB, Agent DB, and Excel sidecar summaries. |
| `GET` | `/api/accounts?limit=60` | List recent account analyses. |
| `GET` | `/api/process` | Load current process state and log tail. |
| `POST` | `/api/run-once` | Start `python -m auto_screen.cli ... once`. |
| `POST` | `/api/start` | Start `python -m auto_screen.cli ... run`. |
| `POST` | `/api/stop` | Stop the launched scan process. |

## 5. File Layout

```text
dashboard/
  __init__.py
  server.py
  static/
    index.html
    styles.css
    app.js
docs/
  dashboard_frontend.md
```

Runtime files:

```text
auto_screen_data/dashboard/auto_screen_process.json
auto_screen_data/dashboard/auto_screen.log
auto_screen_data/progress.json
```

`auto_screen_data/progress.json` is the source for real-time visibility. During leaderboard discovery it exposes the shard name, offset, page size, unique candidate count, newly discovered count, and early-stop reason. During account processing it exposes the exact `current_account`, label, batch index, score, grade, and action.

## 6. Extension Points

- Add account detail pages by exposing report JSON or Markdown through a read-only API.
- Add ServerChan push test buttons once the user confirms the SendKey handling policy.
- Add charts for score distribution, alert trend, and skipped reason distribution.
- Add authenticated remote access only after network exposure, secrets, and permission boundaries are explicitly designed.

## 7. Verification

Static checks:

```powershell
python -m compileall -q dashboard auto_screen agent_core tests
```

Full tests:

```powershell
python -m unittest discover -s tests -v
pytest -q
```
