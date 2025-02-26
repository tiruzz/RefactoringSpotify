import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "3cb0c68445c2438e9facc310b7b0e827"
SPOTIFY_CLIENT_SECRET = "10564376edbe42dda53de2a6be0024a0"
SPOTIFY_REDIRECT_URI = "https://5000-tiruzz-refactoringspoti-8sjla98881e.ws-eu117.gitpod.io/callback"

sp_oauth = SpotifyOAuth(
client_id=SPOTIFY_CLIENT_ID,
client_secret=SPOTIFY_CLIENT_SECRET,
redirect_uri=SPOTIFY_REDIRECT_URI,
scope="user-read-private playlist-read-private",
show_dialog=True 
)

def get_spotify_object(token_info):
    return spotipy.Spotify( auth=token_info['access_token'])

def get_spotify_client():
    token_info = session.get("token_info") 
    if token_info:
        return spotipy.Spotify(auth=token_info.get("access_token"))
    return spotipy.Spotify(auth=None)