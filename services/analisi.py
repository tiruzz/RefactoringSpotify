from services.spotify_api import get_playlist_details
import matplotlib.pyplot as plt
from collections import Counter
import io
import base64

def analizza_brani_per_artista(playlist_id):
    """Analizza il numero di brani per artista in una playlist."""
    playlist_name, brani = get_playlist_details(playlist_id)
    if not brani:
        print("Nessun brano trovato nella playlist.")
        return
    
    artist_count = Counter()
    
    for brano in brani:
        track_info = brano.get('track')
        if track_info:
            for artist in track_info.get('artists', []):
                artist_count[artist['name']] += 1
    
    if not artist_count:
        print("Nessun artista trovato nei brani della playlist.")
        return
    
    # Ordina gli artisti per numero di brani
    artisti, conteggi = zip(*artist_count.most_common(10))  # Primi 10 artisti
    
    # Creazione del grafico con sfondo nero e scritte bianche
    plt.figure(figsize=(10, 5))
    plt.style.use("dark_background")
    plt.barh(artisti[::-1], conteggi[::-1], color='skyblue')  # Inverti per visualizzare bene
    plt.xlabel("Numero di Brani", color='white')
    plt.ylabel("Artisti", color='white')
    plt.title(f"Numero di Brani per Artista nella Playlist: {playlist_name}", color='white')
    plt.xticks(color='white')
    plt.yticks(color='white')
    plt.show()
    
    # Salva il grafico in un buffer di memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return img_base64  # Restituisce l'immagine in formato base64
