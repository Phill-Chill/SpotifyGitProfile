"""
main.py -- Ponto de entrada do GitHub Actions
"""
from __future__ import annotations
import logging, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from spotify_client import from_env
from svg_builder import build_svg, save_svg
from history_manager import save_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

def parse_now_playing(data):
    if not data or data.get("currently_playing_type") != "track":
        return None
    item = data.get("item") or {}
    return {
        "title":     item.get("name", "Desconhecida"),
        "artist":    ", ".join(a["name"] for a in item.get("artists", [])),
        "album":     (item.get("album") or {}).get("name", ""),
        "image_url": ((item.get("album") or {}).get("images", [{}])[0].get("url")),
    }

def parse_recently_played(data):
    items = data.get("items", [])
    if not items: return None
    track = items[0]["track"]
    return {
        "title":     track.get("name", "Desconhecida"),
        "artist":    ", ".join(a["name"] for a in track.get("artists", [])),
        "album":     (track.get("album") or {}).get("name", ""),
        "image_url": ((track.get("album") or {}).get("images", [{}])[0].get("url")),
    }

def parse_top_tracks(data):
    return [
        {"name": t["name"], "artist": ", ".join(a["name"] for a in t.get("artists", [])), "ms": t.get("duration_ms", 0)}
        for t in data.get("items", [])
    ]

def parse_top_artists(data):
    return [{"name": a["name"], "genres": a.get("genres", [])} for a in data.get("items", [])]

def main():
    log.info("Iniciando atualizacao de Spotify Stats...")
    client   = from_env()
    profile  = client.get_current_user()
    username = profile.get("display_name") or profile.get("id", "Usuario")

    # Now playing / fallback para recently played
    now_playing = parse_now_playing(client.get_now_playing())
    if not now_playing:
        now_playing = parse_recently_played(client.get_recently_played(limit=50))

    # Top tracks nos 3 periodos
    top_tracks_short  = parse_top_tracks(client.get_top_tracks(time_range="short_term",  limit=5))
    top_tracks_medium = parse_top_tracks(client.get_top_tracks(time_range="medium_term", limit=5))
    top_tracks_long   = parse_top_tracks(client.get_top_tracks(time_range="long_term",   limit=5))

    # Top artists nos 3 periodos
    top_artists_short  = parse_top_artists(client.get_top_artists(time_range="short_term",  limit=5))
    top_artists_medium = parse_top_artists(client.get_top_artists(time_range="medium_term", limit=5))
    top_artists_long   = parse_top_artists(client.get_top_artists(time_range="long_term",   limit=5))

    # Tempo estimado ouvido
    listening_time = client.get_estimated_listening_time()
    log.info("Tempo estimado ouvido: %s", listening_time)

    # Album art
    album_art_b64 = None
    if now_playing and now_playing.get("image_url"):
        try:
            album_art_b64 = client.get_album_art_b64(now_playing["image_url"])
        except Exception as e:
            log.warning("Falha ao baixar album art: %s", e)

    save_snapshot(top_tracks_short, top_artists_short, now_playing)

    path = save_svg(build_svg(
        username=username,
        now_playing=now_playing,
        top_tracks_short=top_tracks_short,
        top_tracks_medium=top_tracks_medium,
        top_tracks_long=top_tracks_long,
        top_artists_short=top_artists_short,
        top_artists_medium=top_artists_medium,
        top_artists_long=top_artists_long,
        album_art_b64=album_art_b64,
        listening_time=listening_time,
    ))
    log.info("Card gerado: %s", path)

if __name__ == "__main__":
    main()