from __future__ import annotations

import tempfile
import time
import unittest
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from auto_screen.config import load_config
from auto_screen.housekeeping import perform_storage_cleanup
from auto_screen.state_store import StateStore


def _utc_iso_days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


class StorageCleanupTests(unittest.TestCase):
    def test_cleanup_removes_old_archives_and_non_protected_accounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "auto_screen_data"
            accounts_dir = data_dir / "accounts"
            accounts_dir.mkdir(parents=True, exist_ok=True)

            archive_old = root / "archive_reset_older"
            archive_old.mkdir(parents=True, exist_ok=True)
            (archive_old / "payload.txt").write_text("x" * 1024, encoding="utf-8")

            archive_new = root / "archive_reset_latest"
            archive_new.mkdir(parents=True, exist_ok=True)
            (archive_new / "payload.txt").write_text("x" * 1024, encoding="utf-8")

            old_ts = time.time() - 40 * 86400
            now_ts = time.time()
            for path in (archive_old, archive_old / "payload.txt"):
                path.touch(exist_ok=True)
                os.utime(path, (old_ts, old_ts))
            for path in (archive_new, archive_new / "payload.txt"):
                path.touch(exist_ok=True)
                os.utime(path, (now_ts, now_ts))

            account_a = accounts_dir / "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            account_b = accounts_dir / "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
            for account_dir in (account_a, account_b):
                account_dir.mkdir(parents=True, exist_ok=True)
                (account_dir / "account_analysis.json").write_text("{}", encoding="utf-8")

            state_db = root / "state.sqlite3"
            store = StateStore(state_db)
            store.record_alert(str(account_b.name), 66, "B", "title", "message", push_status="sent")
            store.close()

            cfg = load_config(None)
            cfg["data_dir"] = str(data_dir)
            cfg["state_db"] = str(state_db)
            cfg["progress_path"] = str(data_dir / "progress.json")
            cfg["storage_cleanup"] = {
                "enabled": True,
                "min_free_gb": 0.1,
                "archives_keep_latest": 1,
                "archives_max_age_days": 365,
                "accounts_keep_latest": 0,
                "accounts_max_age_days": 0,
                "protect_pushed_accounts": True,
                "log_paths": [],
            }

            summary = perform_storage_cleanup(cfg, reason="test", include_sqlite=False)
            self.assertTrue(summary["enabled"])
            self.assertFalse((root / "archive_reset_older").exists())
            self.assertTrue((root / "archive_reset_latest").exists())
            self.assertFalse(account_a.exists())
            self.assertTrue(account_b.exists())
            self.assertGreaterEqual(summary["actions"]["archives"]["removed"], 1)
            self.assertGreaterEqual(summary["actions"]["accounts"]["removed"], 1)

    def test_cleanup_prunes_old_state_rows_but_keeps_pending_alerts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data_dir = root / "auto_screen_data"
            data_dir.mkdir(parents=True, exist_ok=True)
            state_db = root / "state.sqlite3"
            store = StateStore(state_db)
            conn = store.conn

            conn.execute(
                """
                INSERT INTO runs(address, status, reason, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("0xoldrun", "prefilter_skipped", "old", "{}", _utc_iso_days_ago(120)),
            )
            conn.execute(
                """
                INSERT INTO runs(address, status, reason, payload, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("0xnewrun", "prefilter_skipped", "new", "{}", _utc_iso_days_ago(1)),
            )

            conn.execute(
                """
                INSERT INTO alerts(address, final_score, alert_grade, title, message, created_at, push_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("0xoldsent", 70, "A", "old", "old", _utc_iso_days_ago(120), "sent"),
            )
            conn.execute(
                """
                INSERT INTO alerts(address, final_score, alert_grade, title, message, created_at, push_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("0xoldpending", 70, "A", "old", "old", _utc_iso_days_ago(120), "pending"),
            )
            conn.execute(
                """
                INSERT INTO cycles(started_at, finished_at, status, note)
                VALUES (?, ?, ?, ?)
                """,
                (_utc_iso_days_ago(120), _utc_iso_days_ago(119), "done", "old"),
            )
            conn.commit()
            store.close()

            cfg = load_config(None)
            cfg["data_dir"] = str(data_dir)
            cfg["state_db"] = str(state_db)
            cfg["progress_path"] = str(data_dir / "progress.json")
            cfg["storage_cleanup"] = {
                "enabled": True,
                "runs_retention_days": 30,
                "alerts_retention_days": 30,
                "cycles_retention_days": 30,
                "keep_recent_runs": 500000,
                "keep_recent_alerts": 500000,
                "log_paths": [],
            }

            perform_storage_cleanup(cfg, reason="test", include_sqlite=True)

            verify = StateStore(state_db)
            runs = verify.conn.execute("SELECT address FROM runs ORDER BY id").fetchall()
            alerts = verify.conn.execute("SELECT address, push_status FROM alerts ORDER BY id").fetchall()
            cycles = verify.conn.execute("SELECT status FROM cycles ORDER BY id").fetchall()
            verify.close()

            run_addresses = [row["address"] for row in runs]
            self.assertIn("0xnewrun", run_addresses)
            self.assertNotIn("0xoldrun", run_addresses)

            alert_rows = {(row["address"], row["push_status"]) for row in alerts}
            self.assertIn(("0xoldpending", "pending"), alert_rows)
            self.assertNotIn(("0xoldsent", "sent"), alert_rows)
            self.assertEqual(len(cycles), 0)


if __name__ == "__main__":
    unittest.main()
