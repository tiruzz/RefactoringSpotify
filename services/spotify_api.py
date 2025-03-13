import requests
import spotipy
from flask import session
from spotipy.oauth2 import SpotifyClientCredentials
from services.spotify_oauth import get_spotify_object, sp_oauth, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

def get_user_info():
    token_info = session.get('token_info', None)
    if not token_info:
        return None
    
    sp = get_spotify_object(token_info)
    user_info = sp.current_user()
    playlists = sp.current_user_playlists()
    playlists_info = playlists['items']
    
    return user_info, playlists_info

def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "client_id": SPOTIFY_CLIENT_ID, "client_secret": SPOTIFY_CLIENT_SECRET}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

def get_artist_details(artist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_artist_top_tracks(artist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    response = requests.get(url, headers=headers)
    return response.json().get("tracks", [])

def get_playlist_details(playlist_id):
    token_info = session.get('token_info', None)
    try:
        if token_info:
            sp = get_spotify_object(token_info)
        else:
            client_credentials_manager = SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            )
            sp = spotipy.Spotify(auth_manager=client_credentials_manager)
        
        playlist_data = sp.playlist(playlist_id)
        playlist_name = playlist_data.get('name', 'Nome non disponibile')
        brani = sp.playlist_items(playlist_id)
        brani_specifici = brani.get('items', []) if brani and isinstance(brani, dict) else []
        return playlist_name, brani_specifici
    except spotipy.exceptions.SpotifyException as e:
        print(f"Errore Spotify: {e}")
        return None, None

def search_spotify(query):
    if not query:
        return []
    
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(auth_manager=client_credentials_manager)
    
    search_results = sp.search(q=query, type='artist,track', limit=10)
    results = []
    
    for artist in search_results.get('artists', {}).get('items', []):
        results.append({
            'name': artist['name'],
            'spotify_url': artist['external_urls']['spotify'],
            'image_url': artist['images'][0]['url'] if artist['images'] else 'https://via.placeholder.com/100'
        })
    
    for track in search_results.get('tracks', {}).get('items', []):
        results.append({
            'name': track['name'],
            'spotify_url': track['external_urls']['spotify'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else 'https://via.placeholder.com/100'
        })
    
    return results
