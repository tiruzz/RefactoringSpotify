import requests
import spotipy
from flask import session
from spotipy.oauth2 import SpotifyClientCredentials
from services.spotify_oauth import get_spotify_object, sp_oauth, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from models import Playlist, db
import random
from collections import Counter

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
        
        # Recupera i dati della playlist
        playlist_data = sp.playlist(playlist_id)
        
        # Estrai il nome della playlist
        playlist_name = playlist_data.get('name', 'Nome non disponibile')

        # Recupera l'URL della playlist
        spotify_url = playlist_data.get('external_urls', {}).get('spotify', '#')

        # Recupera gli items (brani) della playlist
        brani = sp.playlist_items(playlist_id)
        brani_specifici = brani.get('items', []) if brani and isinstance(brani, dict) else []
        
        return playlist_name, brani_specifici, spotify_url  # Restituisce anche l'URL di Spotify
    except spotipy.exceptions.SpotifyException as e:
        print(f"Errore Spotify: {e}")
        return None, None, None

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

# Da sistemare

def add_playlist_to_user(playlist_name, playlist_id):
    "Salva l'ID utente e l'ID playlist nel database."
    
    if 'user_id' not in session:
        return "Utente non autenticato", 403

    user_id = session['user_id']

    # Controlla se la playlist è già salvata per l'utente
    existing_entry = Playlist.query.filter_by(user_id=user_id, playlist_id=playlist_id, name=playlist_name).first()
    if existing_entry:
        return "Playlist già aggiunta", 409  # HTTP 409 Conflict

    # Salva la playlist nel database
    new_entry = Playlist(user_id=user_id, playlist_id=playlist_id, name=playlist_name)
    db.session.add(new_entry)
    db.session.commit()

    return "Playlist aggiunta con successo", 200

def get_artist_genres(artist_id):
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
        
        artist = sp.artist(artist_id)
        return artist.get('genres', [])
    except Exception as e:
        print(f"Errore durante il recupero dei generi per {artist_id}: {e}")
        return []

def genera_raccomandazioni_personalizzate(user_id):
    # Importa qui dentro Playlist se necessario
    from models import Playlist

    playlists = Playlist.query.filter_by(user_id=user_id).all()
    if not playlists:
        return []

    generi_raccolti = []

    for playlist in playlists:
        playlist_name, brani_specifici, spotify_url = get_playlist_details(playlist.playlist_id)
        if not brani_specifici:
            continue

        for item in brani_specifici:
            track = item.get('track')
            if not track:
                continue

            artist_info = track.get('artists')
            if not artist_info:
                continue

            artist_id = artist_info[0]['id']
            if artist_id:
                artist_genres = get_artist_genres(artist_id)
                generi_raccolti.extend(artist_genres)

    if not generi_raccolti:
        return []

    generi_contati = Counter(generi_raccolti)
    genere_preferito, _ = generi_contati.most_common(1)[0]

    risultati = search_spotify(genere_preferito)
    random.shuffle(risultati)

    # Qui aggiungo anche l'id da passare al template
    return [{
        "id": item["id"],
        "name": item["name"],
        "image_url": item["image_url"],
        "spotify_url": item["spotify_url"]
    } for item in risultati[:5]]