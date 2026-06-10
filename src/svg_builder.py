"""
svg_builder.py
Constrói o card SVG do Spotify com dados reais do usuário.
"""
from __future__ import annotations
import logging
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)
ASSETS_DIR = Path(__file__).parent.parent / "assets"

GENRE_COLORS = {
    "pop": "#1DB954", "rock": "#E91E63", "hip hop": "#9C27B0",
    "electronic": "#00BCD4", "jazz": "#FF9800", "classical": "#795548",
    "r&b": "#F44336", "indie": "#4CAF50", "metal": "#607D8B",
    "default": "#1DB954",
}

def _escape(text: str) -> str:
    return str(text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def _truncate(text: str, max_len: int = 28) -> str:
    return text if len(text) <= max_len else text[:max_len-1] + "…"

def build_svg(username, now_playing, top_tracks, top_artists, album_art_b64) -> str:
    now_title  = _escape(_truncate(now_playing["title"],  30)) if now_playing else "Nada tocando agora"
    now_artist = _escape(_truncate(now_playing["artist"], 30)) if now_playing else "—"
    now_album  = _escape(_truncate(now_playing.get("album",""), 30)) if now_playing else ""
    dot_color  = "#1DB954" if now_playing else "#555"
    dot_anim   = '<animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>' if now_playing else ""

    art_tag = (
        f'<image href="data:image/jpeg;base64,{album_art_b64}" x="20" y="56" width="64" height="64" clip-path="url(#artClip)"/>'
        if album_art_b64 else
        '<rect x="20" y="56" width="64" height="64" rx="8" fill="#1a1a2e" stroke="#333"/>'
        '<text x="52" y="93" text-anchor="middle" font-size="28">🎵</text>'
    )

    track_rows = ""
    for i, t in enumerate(top_tracks[:5]):
        y = 210 + i * 26
        bar_w = max(4, int(80 * (5-i) / 5))
        track_rows += (
            f'<text x="20" y="{y}" class="rank-num">#{i+1}</text>'
            f'<text x="40" y="{y}" class="track-name">{_escape(_truncate(t["name"],24))}</text>'
            f'<text x="40" y="{y+13}" class="track-artist">{_escape(_truncate(t["artist"],24))}</text>'
            f'<rect x="310" y="{y-12}" width="{bar_w}" height="6" rx="3" fill="#1DB954" opacity="0.7"/>'
        )

    artist_rows = ""
    for i, a in enumerate(top_artists[:5]):
        y = 210 + i * 26
        genre = a.get("genres",[""])[0] if a.get("genres") else ""
        color = next((v for k,v in GENRE_COLORS.items() if k in genre.lower()), GENRE_COLORS["default"])
        artist_rows += (
            f'<text x="430" y="{y}" class="rank-num">#{i+1}</text>'
            f'<text x="450" y="{y}" class="track-name">{_escape(_truncate(a["name"],20))}</text>'
            f'<text x="450" y="{y+13}" class="track-artist" fill="{color}">{_escape(_truncate(genre or "—",20))}</text>'
        )

    updated_at = datetime.now(timezone.utc).strftime("%b %d, %Y · %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="600" height="360" viewBox="0 0 600 360">
  <defs>
    <style>
      .title{{font-family:sans-serif;font-size:13px;font-weight:700;fill:#fff}}
      .subtitle{{font-family:sans-serif;font-size:10px;fill:#aaa}}
      .now-title{{font-family:sans-serif;font-size:14px;font-weight:700;fill:#fff}}
      .now-artist{{font-family:sans-serif;font-size:11px;fill:#1DB954}}
      .now-album{{font-family:sans-serif;font-size:10px;fill:#888}}
      .section-head{{font-family:sans-serif;font-size:11px;font-weight:700;fill:#1DB954;letter-spacing:1px}}
      .rank-num{{font-family:sans-serif;font-size:10px;fill:#555;font-weight:700}}
      .track-name{{font-family:sans-serif;font-size:11px;fill:#ddd;font-weight:600}}
      .track-artist{{font-family:sans-serif;font-size:10px;fill:#888}}
      .divider{{stroke:#222;stroke-width:1}}
      .footer{{font-family:sans-serif;font-size:9px;fill:#444}}
    </style>
    <clipPath id="artClip"><rect x="20" y="56" width="64" height="64" rx="8"/></clipPath>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d0d0d"/>
      <stop offset="100%" stop-color="#121212"/>
    </linearGradient>
    <linearGradient id="hGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#1DB954" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#1DB954" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="600" height="360" rx="16" fill="url(#bgGrad)" stroke="#1a1a1a" stroke-width="1"/>
  <rect width="600" height="46" rx="16" fill="url(#hGrad)"/>
  <circle cx="24" cy="23" r="10" fill="#1DB954"/>
  <path d="M18.5 20.5 Q24 18 29.5 20.5" stroke="black" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M19.5 23 Q24 21 28.5 23"     stroke="black" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M20.5 25.5 Q24 24 27.5 25.5" stroke="black" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <text x="42" y="19" class="title">Spotify Stats</text>
  <text x="42" y="32" class="subtitle">{_escape(username)} · últimas 4 semanas</text>
  <circle cx="570" cy="20" r="5" fill="{dot_color}">{dot_anim}</circle>
  <text x="557" y="35" class="footer" text-anchor="middle">LIVE</text>
  {art_tag}
  <text x="96" y="72"  class="subtitle">TOCANDO AGORA</text>
  <text x="96" y="89"  class="now-title">{now_title}</text>
  <text x="96" y="104" class="now-artist">{now_artist}</text>
  <text x="96" y="117" class="now-album">{now_album}</text>
  <line x1="16" y1="138" x2="584" y2="138" class="divider"/>
  <text x="20"  y="158" class="section-head">TOP MÚSICAS</text>
  <text x="430" y="158" class="section-head">TOP ARTISTAS</text>
  <line x1="16" y1="166" x2="584" y2="166" class="divider" opacity="0.5"/>
  {track_rows}
  {artist_rows}
  <line x1="415" y1="170" x2="415" y2="340" class="divider"/>
  <line x1="16" y1="342" x2="584" y2="342" class="divider"/>
  <text x="300" y="354" class="footer" text-anchor="middle">Atualizado em {updated_at}</text>
</svg>"""

def save_svg(svg_content: str, output_dir: Path = ASSETS_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "spotify-stats.svg"
    path.write_text(svg_content, encoding="utf-8")
    return path