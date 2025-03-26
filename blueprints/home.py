from flask import Blueprint, redirect, request, url_for, session, render_template, flash
from services.spotify_api import get_user_info, get_playlist_details, search_spotify, get_artist_details, get_artist_top_tracks, add_playlist_to_user

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home():
    user_info, playlists_info = get_user_info() or (None, None)
    if not user_info:
        return redirect(url_for('auth.login'))
    return render_template('home.html', user_info=user_info, playlists=playlists_info)

@home_bp.route('/')
def home_page():
    user_info, playlists_info = get_user_info() or (None, None)
    is_logged_in = 'user_id' in session  # Verifica se l'utente ha fatto l'accesso
    return render_template('home-page.html', user_info=user_info, playlists=playlists_info, is_logged_in=is_logged_in)

@home_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('home.home_page'))
    results = search_spotify(query)
    is_logged_in = 'user_id' in session  # Verifica se l'utente ha fatto l'accesso
    return render_template('home-page.html', results=results, is_logged_in=is_logged_in)

@home_bp.route('/add_playlist/<playlist_name>/<playlist_id>')
def add_playlist(playlist_name, playlist_id):
    message, status_code = add_playlist_to_user(playlist_name, playlist_id)
    flash(message, "success" if status_code == 200 else "error")
    return redirect(url_for('home.home_page'))


@home_bp.route('/playlist/<playlist_id>')
def playlist_details(playlist_id):
    playlist_name, brani_specifici = get_playlist_details(playlist_id)
    if not playlist_name:
        return "Playlist non trovata o accesso negato", 404
    return render_template('base.html', brani=brani_specifici, nome=playlist_name)

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
    brani = [{
        "nome": track.get("name", "Sconosciuto"),
        "preview_url": track.get("preview_url", ""),
        "spotify_url": track.get("external_urls", {}).get("spotify", "#")
    } for track in top_tracks]
    return render_template('artista.html', nome=nome, immagine=immagine, generi=generi, popolarita=popolarita, followers=followers, spotify_url=spotify_url, brani=brani)
