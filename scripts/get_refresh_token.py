"""
get_refresh_token.py — Roda UMA VEZ localmente para pegar o refresh_token
Uso:
    export SPOTIFY_CLIENT_ID="..."
    export SPOTIFY_CLIENT_SECRET="..."
    python scripts/get_refresh_token.py
"""
import base64, os, urllib.parse, webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID     = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-currently-playing user-read-recently-played user-top-read"

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        auth_code = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("code",[None])[0]
        self.send_response(200); self.end_headers()
        self.wfile.write(b"<h2>Autorizado! Pode fechar esta aba.</h2>")
    def log_message(self, *args): pass

def main():
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": CLIENT_ID, "response_type": "code",
        "redirect_uri": REDIRECT_URI, "scope": SCOPES,
    })
    print(f"\nAbrindo navegador...\nSe não abrir: {auth_url}\n")
    webbrowser.open(auth_url)
    HTTPServer(("localhost", 8888), CallbackHandler).handle_request()

    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    resp  = requests.post("https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {creds}", "Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "authorization_code", "code": auth_code, "redirect_uri": REDIRECT_URI})
    resp.raise_for_status()

    print("\nSucesso!\n" + "="*60)
    print(f"SPOTIFY_REFRESH_TOKEN={resp.json()['refresh_token']}")
    print("="*60 + "\nAdicione como GitHub Secret!")

if __name__ == "__main__": main()