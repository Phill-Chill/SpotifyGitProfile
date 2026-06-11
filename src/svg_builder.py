"""
svg_builder.py
Constroi o card SVG do Spotify com dados reais do usuario.
Layout expandido: 3 periodos de tempo + tempo estimado ouvido.
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

PERIOD_LABELS = {
    "short_term":  "4 SEMANAS",
    "medium_term": "6 MESES",
    "long_term":   "ALL TIME",
}

def _escape(text: str) -> str:
    return str(text).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','"'&quot;"'"')

def _truncate(text: str, max_len: int = 28) -> str:
    return text if len(text) <= max_len else text[:max_len-1] + "\u2026"

def _track_col(tracks: list, x_rank: int, x_text: int, y_start: int, bar_x: int) -> str:
    rows = ""
    for i, t in enumerate(tracks[:5]):
        y = y_start + i * 28
        bar_w = max(4, int(60 * (5 - i) / 5))
        rows += (
            f'<text x="{x_rank}" y="{y}" class="rank-num">#{i+1}</text>'
            f'<text x="{x_text}" y="{y}" class="track-name">{_escape(_truncate(t["name"], 18))}</text>'
            f'<text x="{x_text}" y="{y+13}" class="track-artist">{_escape(_truncate(t["artist"], 18))}</text>'
            f'<rect x="{bar_x}" y="{y-11}" width="{bar_w}" height="5" rx="2" fill="#1DB954" opacity="0.6"/>'
        )
    return rows

def _artist_col(artists: list, x_rank: int, x_text: int, y_start: int) -> str:
    rows = ""
    for i, a in enumerate(artists[:5]):
        y = y_start + i * 28
        genre = a.get("genres", [""])[0] if a.get("genres") else ""
        color = next((v for k, v in GENRE_COLORS.items() if k in genre.lower()), GENRE_COLORS["default"])
        rows += (
            f'<text x="{x_rank}" y="{y}" class="rank-num">#{i+1}</text>'
            f'<text x="{x_text}" y="{y}" class="track-name">{_escape(_truncate(a["name"], 16))}</text>'
            f'<text x="{x_text}" y="{y+13}" class="track-artist" fill="{color}">{_escape(_truncate(genre or "\u2014", 16))}</text>'
        )
    return rows

def build_svg(
    username: str,
    now_playing: dict | None,
    top_tracks_short: list,
    top_tracks_medium: list,
    top_tracks_long: list,
    top_artists_short: list,
    top_artists_medium: list,
    top_artists_long: list,
    album_art_b64: str | None,
    listening_time: str = "\u2014",
) -> str:

    now_title  = _escape(_truncate(now_playing["title"],  32)) if now_playing else "Nada tocando agora"
    now_artist = _escape(_truncate(now_playing["artist"], 32)) if now_playing else "\u2014"
    now_album  = _escape(_truncate(now_playing.get("album", ""), 32)) if now_playing else ""
    dot_color  = "#1DB954" if now_playing else "#555"
    dot_anim   = '<animate attributeName="opacity" values="1;0.3;1" dur="1.5s" repeatCount="indefinite"/>' if now_playing else ""

    art_tag = (
        f'<image href="data:image/jpeg;base64,{album_art_b64}" x="20" y="58" width="64" height="64" clip-path="url(#artClip)"/>' 
        if album_art_b64 else
        '<rect x="20" y="58" width="64" height="64" rx="8" fill="#1a1a2e" stroke="#333"/>'
        '<text x="52" y="95" text-anchor="middle" font-size="28">\u266b</text>'
    )

    # === Secao de tracks (3 colunas) ===
    col_w   = 186
    y_rows  = 310
    tracks_short_svg  = _track_col(top_tracks_short,  16,       36,       y_rows, 150)
    tracks_medium_svg = _track_col(top_tracks_medium, 16+col_w, 36+col_w, y_rows, 150+col_w)
    tracks_long_svg   = _track_col(top_tracks_long,   16+col_w*2, 36+col_w*2, y_rows, 150+col_w*2)

    # === Secao de artistas (3 colunas) ===
    y_art = 570
    artists_short_svg  = _artist_col(top_artists_short,  16,         36,         y_art)
    artists_medium_svg = _artist_col(top_artists_medium, 16+col_w,   36+col_w,   y_art)
    artists_long_svg   = _artist_col(top_artists_long,   16+col_w*2, 36+col_w*2, y_art)

    updated_at = datetime.now(timezone.utc).strftime("%b %d, %Y · %H:%M UTC")

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="600" height="760" viewBox="0 0 600 760">
  <defs>
    <style>
      .title{{font-family:sans-serif;font-size:13px;font-weight:700;fill:#fff}}
      .subtitle{{font-family:sans-serif;font-size:10px;fill:#aaa}}
      .now-title{{font-family:sans-serif;font-size:14px;font-weight:700;fill:#fff}}
      .now-artist{{font-family:sans-serif;font-size:11px;fill:#1DB954}}
      .now-album{{font-family:sans-serif;font-size:10px;fill:#888}}
      .section-head{{font-family:sans-serif;font-size:10px;font-weight:700;fill:#1DB954;letter-spacing:1px}}
      .period-label{{font-family:sans-serif;font-size:9px;font-weight:700;fill:#555;letter-spacing:1px}}
      .rank-num{{font-family:sans-serif;font-size:10px;fill:#555;font-weight:700}}
      .track-name{{font-family:sans-serif;font-size:10px;fill:#ddd;font-weight:600}}
      .track-artist{{font-family:sans-serif;font-size:9px;fill:#888}}
      .divider{{stroke:#222;stroke-width:1}}
      .footer{{font-family:sans-serif;font-size:9px;fill:#444}}
      .time-label{{font-family:sans-serif;font-size:11px;fill:#aaa}}
      .time-value{{font-family:sans-serif;font-size:13px;font-weight:700;fill:#1DB954}}
    </style>
    <clipPath id="artClip"><rect x="20" y="58" width="64" height="64" rx="8"/></clipPath>
    <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d0d0d"/>
      <stop offset="100%" stop-color="#121212"/>
    </linearGradient>
    <linearGradient id="hGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#1DB954" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#1DB954" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="600" height="760" rx="16" fill="url(#bgGrad)" stroke="#1a1a1a" stroke-width="1"/>
  <rect width="600" height="46" rx="16" fill="url(#hGrad)"/>

  <!-- Header -->
  <circle cx="24" cy="23" r="10" fill="#1DB954"/>
  <path d="M18.5 20.5 Q24 18 29.5 20.5" stroke="black" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M19.5 23 Q24 21 28.5 23"     stroke="black" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M20.5 25.5 Q24 24 27.5 25.5" stroke="black" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <text x="42" y="19" class="title">Spotify Stats</text>
  <text x="42" y="32" class="subtitle">{_escape(username)}</text>
  <circle cx="570" cy="20" r="5" fill="{dot_color}">{dot_anim}</circle>
  <text x="557" y="35" class="footer" text-anchor="middle">LIVE</text>

  <!-- Now Playing -->
  {art_tag}
  <text x="96" y="74"  class="subtitle">TOCANDO AGORA</text>
  <text x="96" y="91"  class="now-title">{now_title}</text>
  <text x="96" y="106" class="now-artist">{now_artist}</text>
  <text x="96" y="119" class="now-album">{now_album}</text>

  <!-- Listening Time -->
  <line x1="16" y1="140" x2="584" y2="140" class="divider"/>
  <text x="20"  y="162" class="time-label">&#9201; Ouvidas recentemente</text>
  <text x="220" y="162" class="time-value">{_escape(listening_time)}</text>

  <!-- Divider tracks -->
  <line x1="16" y1="175" x2="584" y2="175" class="divider"/>
  <text x="300" y="191" class="section-head" text-anchor="middle">TOP MUSICAS</text>
  <line x1="16" y1="198" x2="584" y2="198" class="divider" opacity="0.4"/>

  <!-- Period labels tracks -->
  <text x="{16 + col_w//2}"     y="212" class="period-label" text-anchor="middle">4 SEMANAS</text>
  <text x="{16 + col_w + col_w//2}" y="212" class="period-label" text-anchor="middle">6 MESES</text>
  <text x="{16 + col_w*2 + col_w//2}" y="212" class="period-label" text-anchor="middle">ALL TIME</text>

  <!-- Column dividers tracks -->
  <line x1="{16 + col_w}"   y1="200" x2="{16 + col_w}"   y2="460" class="divider" opacity="0.4"/>
  <line x1="{16 + col_w*2}" y1="200" x2="{16 + col_w*2}" y2="460" class="divider" opacity="0.4"/>

  {tracks_short_svg}
  {tracks_medium_svg}
  {tracks_long_svg}

  <!-- Divider artists -->
  <line x1="16" y1="470" x2="584" y2="470" class="divider"/>
  <text x="300" y="488" class="section-head" text-anchor="middle">TOP ARTISTAS</text>
  <line x1="16" y1="496" x2="584" y2="496" class="divider" opacity="0.4"/>

  <!-- Period labels artists -->
  <text x="{16 + col_w//2}"     y="510" class="period-label" text-anchor="middle">4 SEMANAS</text>
  <text x="{16 + col_w + col_w//2}" y="510" class="period-label" text-anchor="middle">6 MESES</text>
  <text x="{16 + col_w*2 + col_w//2}" y="510" class="period-label" text-anchor="middle">ALL TIME</text>

  <!-- Column dividers artists -->
  <line x1="{16 + col_w}"   y1="496" x2="{16 + col_w}"   y2="740" class="divider" opacity="0.4"/>
  <line x1="{16 + col_w*2}" y1="496" x2="{16 + col_w*2}" y2="740" class="divider" opacity="0.4"/>

  {artists_short_svg}
  {artists_medium_svg}
  {artists_long_svg}

  <!-- Footer -->
  <line x1="16" y1="742" x2="584" y2="742" class="divider"/>
  <text x="300" y="754" class="footer" text-anchor="middle">Atualizado em {updated_at}</text>
</svg>"""

def save_svg(svg_content: str, output_dir: Path = ASSETS_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "spotify-stats.svg"
    path.write_text(svg_content,