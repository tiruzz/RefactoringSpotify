from flask import Blueprint, redirect, request, url_for, session, render_template
import spotipy
import requests
from services.spotify_oauth import get_spotify_object, sp_oauth, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from spotipy.oauth2 import SpotifyClientCredentials

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('auth.login')) 

    sp = get_spotify_object(token_info)
    user_info = sp.current_user()
    playlists = sp.current_user_playlists() 
    playlists_info = playlists['items'] 
    
    return render_template('home.html', user_info=user_info, playlists=playlists_info)

@home_bp.route('/')
def home_page():
    return render_template('home-page.html')

@home_bp.route('/playlist/<playlist_id>')
def playlist_details(playlist_id):
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
        
        # Recupera la playlist completa
        playlist_data = sp.playlist(playlist_id)
        playlist_name = playlist_data.get('name', 'Nome non disponibile')

        brani = sp.playlist_items(playlist_id)
        brani_specifici = brani.get('items', []) if brani and isinstance(brani, dict) else []
    except spotipy.exceptions.SpotifyException as e:
        print(f"Errore Spotify: {e}")
        return "Playlist non trovata o accesso negato", 404
    
    return render_template('base.html', brani=brani_specifici, nome=playlist_name)

# Funzione per ottenere il token di accesso senza autenticazione utente
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials", "client_id": SPOTIFY_CLIENT_ID, "client_secret": SPOTIFY_CLIENT_SECRET}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# Funzione per ottenere i dettagli dell'artista
def get_artist_details(artist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    response = requests.get(url, headers=headers)
    return response.json()

# Funzione per ottenere i brani più popolari dell'artista
def get_artist_top_tracks(artist_id):
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
    response = requests.get(url, headers=headers)
    return response.json().get("tracks", [])

@home_bp.route('/artist/<artist_id>')
def artist_details(artist_id):
    artist = get_artist_details(artist_id)
    top_tracks = get_artist_top_tracks(artist_id)
    
    if 'error' in artist:
        return "Artista non trovato", 404
    
    nome = artist.get("name", "Sconosciuto")
    immagine = artist.get("images", [{}])[0].get("url", "")
    generi = ', '.join(artist.get('genres', ['Non disponibile']))
    popolarita = artist.get("popularity", "Sconosciuta")
    followers = artist.get("followers", {}).get("total", "Sconosciuto")
    spotify_url = artist.get("external_urls", {}).get("spotify", "#")
    
    # Estrarre i dettagli delle tracce
    brani = [{
        "nome": track.get("name", "Sconosciuto"),
        "preview_url": track.get("preview_url", ""),
        "spotify_url": track.get("external_urls", {}).get("spotify", "#")
    } for track in top_tracks]
    
    return render_template('artista.html', nome=nome, immagine=immagine, generi=generi, popolarita=popolarita, followers=followers, spotify_url=spotify_url, brani=brani)

# Aggiungi una nuova route per la ricerca
@home_bp.route('/search')
def search_results():
    query = request.args.get('query', '')
    
    if query:
        # Se l'utente è loggato, usa il suo token, altrimenti usa il client Spotify
        token_info = session.get('token_info', None)
        if token_info:
            sp = get_spotify_object(token_info)  # Oggetto Spotify con token utente
        else:
            # Usa le credenziali client se non autenticato
            sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            ))
        
        # Esegui la ricerca per artisti e playlist
        search_results = sp.search(q=query, type='artist,playlist', limit=10)
        
        # Gestisci i risultati per artisti e playlist separatamente
        artists = search_results.get('artists', {}).get('items', [])
        playlists = search_results.get('playlists', {}).get('items', [])
        
        # Aggiungi la logica per controllare che 'external_urls' esista
        for artist in artists:
            if artist:
                external_urls = artist.get('external_urls', None)
                if external_urls and isinstance(external_urls, dict):
                    artist['external_urls'] = external_urls.get('spotify', '#')
                else:
                    artist['external_urls'] = '#'
                artist['images'] = artist.get('images', [{}])[0].get('url', 'https://via.placeholder.com/150')
                artist['name'] = artist.get('name', 'Nome non disponibile')

        for playlist in playlists:
            if playlist:
                external_urls = playlist.get('external_urls', None)
                if external_urls and isinstance(external_urls, dict):
                    playlist['external_urls'] = external_urls.get('spotify', '#')
                else:
                    playlist['external_urls'] = '#'
                playlist['images'] = playlist.get('images', [{}])[0].get('url', 'https://via.placeholder.com/150')
                playlist['name'] = playlist.get('name', 'Nome non disponibile')

        # Passa i risultati ai template
        return render_template('search_results.html', artists=artists, playlists=playlists)
    
    # Se la query è vuota, ritorna alla home
    return redirect(url_for('home.home'))




