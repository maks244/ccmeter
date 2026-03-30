"""Scan Claude Code JSONL files for per-message token usage and activity."""

import json
import platform
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from ccmeter.activity import ActivityEvent, extract_activity
from ccmeter.display import progress, progress_done

CLAUDE_DIR = Path.home() / ".claude" / "projects"


@dataclass
class TokenEvent:
    ts: str
    input_tokens: int
    output_tokens: int
    cache_read: int
    cache_create: int
    model: str
    session_id: str
    cc_version: str


@dataclass
class ScanResult:
    events: list[TokenEvent] = field(default_factory=list)
    activity: list[ActivityEvent] = field(default_factory=list)
    cc_versions: set[str] = field(default_factory=set)
    models: set[str] = field(default_factory=set)
    sessions: int = 0
    os: str = field(default_factory=lambda: platform.system().lower())


def scan(days: int = 30) -> ScanResult:
    """Scan all JSONL files for token events and activity within the lookback window."""
    cutoff = (datetime.now(tz=UTC) - timedelta(days=days)).isoformat()
    result = ScanResult()
    seen_sessions = set()

    if not CLAUDE_DIR.exists():
        return result

    cutoff_ts = (datetime.now(tz=UTC) - timedelta(days=days)).timestamp()
    files = [f for f in CLAUDE_DIR.glob("*/*.jsonl") if f.stat().st_mtime >= cutoff_ts]
    tty = sys.stdout.isatty()
    total = len(files)

    if tty and total:
        progress(total, 0, "scan")

    for i, jsonl in enumerate(files):
        _scan_file(jsonl, cutoff, result, seen_sessions)
        if tty and total:
            progress(total, i + 1, "scan")

    if tty and total:
        progress_done("scan")

    result.sessions = len(seen_sessions)
    result.events.sort(key=lambda e: e.ts)
    return result


def _scan_file(path: Path, cutoff: str, result: ScanResult, seen_sessions: set):
    try:
        with path.open() as f:
            for line in f:
                if '"usage"' not in line and '"tool_use"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue

                ts = d.get("timestamp", "")
                if not ts or ts < cutoff:
                    continue

                msg_type = d.get("type", "")
                msg = d.get("message")
                if not isinstance(msg, dict):
                    continue

                # Token extraction (assistant messages with usage)
                usage = msg.get("usage")
                if usage:
                    session_id = d.get("sessionId", "")
                    cc_version = d.get("version", "")
                    model = msg.get("model", "")

                    if session_id:
                        seen_sessions.add(session_id)
                    if cc_version:
                        result.cc_versions.add(cc_version)
                    if model:
                        result.models.add(model)

                    result.events.append(
                        TokenEvent(
                            ts=ts,
                            input_tokens=usage.get("input_tokens", 0),
                            output_tokens=usage.get("output_tokens", 0),
                            cache_read=usage.get("cache_read_input_tokens", 0),
                            cache_create=usage.get("cache_creation_input_tokens", 0),
                            model=model,
                            session_id=session_id,
                            cc_version=cc_version,
                        )
                    )

                # Activity extraction (tool_use blocks in any message)
                act = extract_activity(d, msg_type, msg)
                if act:
                    result.activity.append(act)
    except OSError:
        pass
