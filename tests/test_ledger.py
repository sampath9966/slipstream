"""Tests for slipstream ledger math and transcript parsing."""

import json
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import importlib.util
import importlib.machinery

import pytest

# Load bin/slipstream (no .py extension) as a module
_engine_path = str(Path(__file__).parent.parent / "bin" / "slipstream")
_loader = importlib.machinery.SourceFileLoader("slipstream", _engine_path)
_spec = importlib.util.spec_from_loader("slipstream", _loader)
ss = importlib.util.module_from_spec(_spec)
_loader.exec_module(ss)


# ---------------------------------------------------------------------------
# Transcript parsing
# ---------------------------------------------------------------------------

def write_transcript(lines: list, tmp_path: Path) -> Path:
    p = tmp_path / "transcript.jsonl"
    p.write_text("\n".join(json.dumps(l) for l in lines) + "\n")
    return p


class TestTranscriptParsing:
    def test_format1_role_assistant(self, tmp_path):
        t = write_transcript([
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi", "model": "claude-opus-5",
             "usage": {"input_tokens": 100, "output_tokens": 50,
                       "cache_creation_input_tokens": 200, "cache_read_input_tokens": 300}},
        ], tmp_path)
        u = ss.parse_transcript(str(t))
        assert u["input_tokens"] == 100
        assert u["output_tokens"] == 50
        assert u["cache_write_tokens"] == 200
        assert u["cache_read_tokens"] == 300
        assert u["model"] == "claude-opus-5"

    def test_format2_type_assistant(self, tmp_path):
        t = write_transcript([
            {"type": "user", "message": {"content": "hello"}},
            {"type": "assistant", "message": {
                "model": "claude-sonnet-5",
                "usage": {"input_tokens": 42, "output_tokens": 17,
                          "cache_creation_input_tokens": 0, "cache_read_input_tokens": 5},
            }},
        ], tmp_path)
        u = ss.parse_transcript(str(t))
        assert u["input_tokens"] == 42
        assert u["output_tokens"] == 17
        assert u["cache_read_tokens"] == 5
        assert u["model"] == "claude-sonnet-5"

    def test_missing_file(self, tmp_path):
        u = ss.parse_transcript(str(tmp_path / "nope.jsonl"))
        assert u == {}

    def test_empty_file(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text("")
        u = ss.parse_transcript(str(t))
        assert u == {}

    def test_picks_last_assistant_turn(self, tmp_path):
        t = write_transcript([
            {"role": "assistant", "usage": {"input_tokens": 10, "output_tokens": 5}},
            {"role": "user", "content": "more"},
            {"role": "assistant", "usage": {"input_tokens": 99, "output_tokens": 33}},
        ], tmp_path)
        u = ss.parse_transcript(str(t))
        assert u["input_tokens"] == 99

    def test_malformed_lines_skipped(self, tmp_path):
        t = tmp_path / "transcript.jsonl"
        t.write_text('not json\n{"role":"assistant","usage":{"input_tokens":7,"output_tokens":3}}\n')
        u = ss.parse_transcript(str(t))
        assert u["input_tokens"] == 7


# ---------------------------------------------------------------------------
# DB / ledger math
# ---------------------------------------------------------------------------

class TestLedger:
    def setup_method(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db_file = Path(self._tmp.name) / "test.db"

    def teardown_method(self):
        self._tmp.cleanup()

    def open(self):
        return ss.open_db(self.db_file)

    def test_schema_created(self):
        conn = self.open()
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        assert "turns" in tables
        assert "tool_uses" in tables

    def test_insert_turn(self):
        conn = self.open()
        conn.execute(
            """INSERT INTO turns (session_id, ts, input_tokens, output_tokens,
               cache_read_tokens, cache_write_tokens) VALUES (?,?,?,?,?,?)""",
            ("s1", time.time(), 100, 50, 20, 10),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM turns WHERE session_id='s1'").fetchone()
        assert row["input_tokens"] == 100
        assert row["output_tokens"] == 50

    def test_total_tokens_sum(self):
        conn = self.open()
        now = time.time()
        for i in range(5):
            conn.execute(
                """INSERT INTO turns (session_id, ts, input_tokens, output_tokens,
                   cache_read_tokens, cache_write_tokens) VALUES (?,?,?,?,?,?)""",
                ("sess", now - i * 10, 100, 50, 0, 0),
            )
        conn.commit()
        row = conn.execute(
            "SELECT SUM(input_tokens + output_tokens) as total FROM turns WHERE session_id='sess'"
        ).fetchone()
        assert row["total"] == 750  # 5 * 150

    def test_tool_use_insert(self):
        conn = self.open()
        conn.execute(
            "INSERT INTO tool_uses (session_id, tool_name, file_paths, ts) VALUES (?,?,?,?)",
            ("s1", "Read", json.dumps(["/foo/bar.py"]), time.time()),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tool_uses WHERE session_id='s1'").fetchone()
        assert row["tool_name"] == "Read"
        paths = json.loads(row["file_paths"])
        assert "/foo/bar.py" in paths

    def test_per_file_aggregation(self):
        conn = self.open()
        now = time.time()
        files = ["/a.py", "/b.py", "/a.py", "/a.py", "/b.py"]
        for f in files:
            conn.execute(
                "INSERT INTO tool_uses (session_id, tool_name, file_paths, ts) VALUES (?,?,?,?)",
                ("s1", "Read", json.dumps([f]), now),
            )
        conn.commit()
        rows = conn.execute(
            "SELECT file_paths, COUNT(*) as c FROM tool_uses GROUP BY file_paths ORDER BY c DESC"
        ).fetchall()
        # /a.py appears 3 times
        assert json.loads(rows[0]["file_paths"]) == ["/a.py"]
        assert rows[0]["c"] == 3


# ---------------------------------------------------------------------------
# File path extraction
# ---------------------------------------------------------------------------

class TestFilePathExtraction:
    def test_read_tool(self):
        paths = ss._extract_file_paths("Read", {"file_path": "/foo.py"})
        assert paths == ["/foo.py"]

    def test_edit_tool(self):
        paths = ss._extract_file_paths("Edit", {"file_path": "/bar.py", "old_string": "x", "new_string": "y"})
        assert "/bar.py" in paths

    def test_bash_no_paths(self):
        paths = ss._extract_file_paths("Bash", {"command": "ls -la"})
        assert paths == []

    def test_glob_uses_pattern(self):
        paths = ss._extract_file_paths("Glob", {"pattern": "**/*.py"})
        assert "**/*.py" in paths

    def test_deduplication(self):
        paths = ss._extract_file_paths("Edit", {"file_path": "/a.py", "path": "/a.py"})
        assert paths.count("/a.py") == 1


# ---------------------------------------------------------------------------
# Pacing governor
# ---------------------------------------------------------------------------

class TestPacingGovernor:
    def cfg(self, threshold=60, max_delay=300):
        return {"pacing_threshold_pct": threshold, "pacing_max_delay": max_delay}

    def test_below_threshold_returns_zero(self):
        assert ss.pace_delay(0.0, self.cfg()) == 0.0
        assert ss.pace_delay(59.9, self.cfg()) == 0.0

    def test_at_threshold_returns_zero(self):
        assert ss.pace_delay(60.0, self.cfg()) == 0.0

    def test_at_100pct_returns_max_delay(self):
        assert ss.pace_delay(100.0, self.cfg()) == 300.0

    def test_midpoint_returns_half_max(self):
        # threshold=60, max=300 → midpoint at 80% → 150 s
        result = ss.pace_delay(80.0, self.cfg())
        assert abs(result - 150.0) < 0.01

    def test_custom_threshold(self):
        # threshold=80, max=60 → at 90% (halfway) → 30 s
        result = ss.pace_delay(90.0, self.cfg(threshold=80, max_delay=60))
        assert abs(result - 30.0) < 0.01

    def test_above_100_clamped_to_max(self):
        assert ss.pace_delay(110.0, self.cfg()) == 300.0

    def test_zero_max_delay(self):
        assert ss.pace_delay(100.0, self.cfg(max_delay=0)) == 0.0
