from flask import Blueprint, redirect, request, url_for, session, render_template
import spotipy
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
        
        brani = sp.playlist_items(playlist_id)
        brani_specifici = brani.get('items', []) if brani and isinstance(brani, dict) else []
    except spotipy.exceptions.SpotifyException as e:
        print(f"Errore Spotify: {e}")
        return "Playlist non trovata o accesso negato", 404
    
    return render_template('base.html', brani=brani_specifici)



@home_bp.route('/artist/<artist_id>')
def artist_details(artist_id):

    return render_template('artista.html', biografia=biografia)
