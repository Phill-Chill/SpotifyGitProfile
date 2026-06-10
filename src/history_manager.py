"""
history_manager.py — Salva histórico em JSON
"""
from __future__ import annotations
import json, logging
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)
DATA_DIR     = Path(__file__).parent.parent / "data"
HISTORY_FILE = DATA_DIR / "history.json"

def load_history() -> dict:
    if not HISTORY_FILE.exists(): return {"snapshots": []}
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))

def save_snapshot(top_tracks, top_artists, now_playing) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    history = load_history()
    history["snapshots"].append({
        "timestamp":   datetime.now(timezone.utc).isoformat(),
        "now_playing": now_playing,
        "top_tracks":  top_tracks,
        "top_artists": top_artists,
    })
    history["snapshots"] = history["snapshots"][-30:]
    HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")