from services.spotify_api import get_playlist_details
import matplotlib.pyplot as plt
from collections import Counter
import io
import base64
import numpy as np

def salva_grafico():
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return img_base64

def analizza_playlist(playlist_id):
    playlist_name, brani = get_playlist_details(playlist_id)
    if not brani:
        return {}
    
    anni = []
    durate = []
    popolarita = []
    generi = Counter()
    
    for brano in brani:
        track = brano.get('track', {})
        anni.append(track.get('album', {}).get('release_date', '0')[:4])
        durate.append(track.get('duration_ms', 0) / 1000)  # Converti in secondi
        popolarita.append(track.get('popularity', 0))
        for artist in track.get('artists', []):
            generi.update(artist.get('genres', []))
    
    # Grafico Distribuzione Anni
    plt.figure()
    plt.hist([int(a) for a in anni if a.isdigit()], bins=20, color='skyblue')
    plt.xlabel("Anno di Pubblicazione")
    plt.ylabel("Numero di Brani")
    plt.title("Distribuzione Temporale dei Brani")
    distribuzione_anni = salva_grafico()
    
    # Grafico Distribuzione Durata
    plt.figure()
    plt.hist(durate, bins=20, color='lightcoral')
    plt.xlabel("Durata (secondi)")
    plt.ylabel("Numero di Brani")
    plt.title("Distribuzione della Durata dei Brani")
    distribuzione_durate = salva_grafico()
    
    # Grafico Distribuzione Popolarità
    plt.figure()
    plt.hist(popolarita, bins=20, color='gold')
    plt.xlabel("Livello di Popolarità")
    plt.ylabel("Numero di Brani")
    plt.title("Distribuzione della Popolarità")
    distribuzione_popolarita = salva_grafico()
    
    # Grafico Distribuzione Generi
    plt.figure()
    generi_comuni = generi.most_common(10)
    if generi_comuni:
        labels, counts = zip(*generi_comuni)
        plt.barh(labels[::-1], counts[::-1], color='lightgreen')
        plt.xlabel("Numero di Brani")
        plt.ylabel("Generi")
        plt.title("Distribuzione dei Generi Musicali")
    distribuzione_generi = salva_grafico()
    
    # Grafico Evoluzione Popolarità
    plt.figure()
    anni_num = [int(a) for a in anni if a.isdigit()]
    if anni_num:
        plt.scatter(anni_num, popolarita, color='deepskyblue', alpha=0.5)
        z = np.polyfit(anni_num, popolarita, 1)
        p = np.poly1d(z)
        plt.plot(sorted(anni_num), p(sorted(anni_num)), "r--")
        plt.xlabel("Anno di Pubblicazione")
        plt.ylabel("Popolarità")
        plt.title("Evoluzione della Popolarità nel Tempo")
    evoluzione_popolarita = salva_grafico()
    
    return {
        "distribuzione_anni": distribuzione_anni,
        "distribuzione_durate": distribuzione_durate,
        "distribuzione_popolarita": distribuzione_popolarita,
        "distribuzione_generi": distribuzione_generi,
        "evoluzione_popolarita": evoluzione_popolarita
    }
