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
    
    # Cerca solo playlist pubbliche -Amine
    search_results = sp.search(q=query, type='playlist', limit=10)
    results = []
    
    #Rielabora i risultati per poi rispedirli in una variabile "results" -Amine
    for playlist in search_results.get('playlists', {}).get('items', []):
        if playlist and playlist.get('public') is not None and playlist['public']:  # Controllo sicurezza
            results.append({
                'id': playlist['id'],
                'name': playlist['name'],
                'spotify_url': playlist['external_urls']['spotify'],
                'image_url': playlist['images'][0]['url'] if playlist.get('images') else 'https://via.placeholder.com/100'
            })
    
    # Ritorna la variabile -Amine
    return results



#Funzione per estrapolare le playlist dell'utente e inserirle nel database in modo parziale da migliorare e rendere efficiente col sito e la struttura -Amine
def save_user_playlists():
    if 'spotify_token' not in session:
        return "Token non trovato", 403

    sp = spotipy.Spotify(auth=session['spotify_token'])

    # Ottieni l'ID utente Spotify
    user_spotify_data = sp.current_user()
    spotify_user_id = user_spotify_data['id']

    # Controlla l'utente
    user = User.query.filter_by(username=spotify_user_id).first()
    if not user:
        user = User(username=spotify_user_id, password="")
        db.session.add(user)
        db.session.commit()

    
    # Ottieni le playlist dell'utente che ha effettuato l'acceso su spotify
    playlists = sp.current_user_playlists()['items']

    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_name = playlist['name']

        # Controlla se la playlist è già nel DB
        existing_playlist = Playlist.query.filter_by(playlist_id=playlist_id, user_id=user.id).first()
        if not existing_playlist:
            new_playlist = Playlist(user_id=user.id, playlist_id=playlist_id, name=playlist_name)
            db.session.add(new_playlist)

    db.session.commit()