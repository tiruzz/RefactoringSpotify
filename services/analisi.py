from services.spotify_api import get_playlist_details, get_artist_genres
import matplotlib.pyplot as plt
from collections import Counter
import io
import base64
import numpy as np
import requests

def salva_grafico():
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches='tight')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return img_base64

def analizza_playlist(playlist_id):
    playlist_name, brani, spotify_url = get_playlist_details(playlist_id)
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


def confronta_due_playlist(playlist1_id, playlist2_id):
    nome1, brani1, link1 = get_playlist_details(playlist1_id)
    nome2, brani2, link2 = get_playlist_details(playlist2_id)

    if not brani1 or not brani2:
        return {"errore": "Una o entrambe le playlist sono vuote."}

    # Set per confronto rapido
    titoli1 = set((b['track']['name'], b['track']['artists'][0]['name']) for b in brani1)
    titoli2 = set((b['track']['name'], b['track']['artists'][0]['name']) for b in brani2)
    brani_comuni = titoli1 & titoli2

    artisti1 = set(a['name'] for b in brani1 for a in b['track']['artists'])
    artisti2 = set(a['name'] for b in brani2 for a in b['track']['artists'])
    artisti_comuni = artisti1 & artisti2

    popolarita1 = [b['track']['popularity'] for b in brani1 if 'popularity' in b['track']]
    popolarita2 = [b['track']['popularity'] for b in brani2 if 'popularity' in b['track']]
    pop_avg_1 = sum(popolarita1) / len(popolarita1)
    pop_avg_2 = sum(popolarita2) / len(popolarita2)

    # Generi e Anni
    generi1 = Counter()
    generi2 = Counter()
    anni1 = []
    anni2 = []

    for b in brani1:
        anni1.append(b['track']['album']['release_date'][:4])
        for a in b['track']['artists']:
            generi1.update(get_artist_genres(a['id']))

    for b in brani2:
        anni2.append(b['track']['album']['release_date'][:4])
        for a in b['track']['artists']:
            generi2.update(get_artist_genres(a['id']))

    # Grafico comparativo popolarità
    plt.figure()
    plt.bar(['Playlist 1', 'Playlist 2'], [pop_avg_1, pop_avg_2], color=['steelblue', 'orange'])
    plt.ylabel("Popolarità Media")
    plt.title("Confronto Popolarità Media")
    grafico_pop = salva_grafico()

    # Grafico distribuzione temporale
    plt.figure()
    anni1_num = [int(a) for a in anni1 if a.isdigit()]
    anni2_num = [int(a) for a in anni2 if a.isdigit()]
    plt.hist([anni1_num, anni2_num], bins=20, label=[nome1, nome2], color=['blue', 'green'], alpha=0.7)
    plt.legend()
    plt.title("Distribuzione Temporale")
    plt.xlabel("Anno")
    plt.ylabel("Numero Brani")
    grafico_anni = salva_grafico()

    # Grafico generi
    plt.figure()
    g1 = generi1.most_common(5)
    g2 = generi2.most_common(5)
    labels = list(set([g for g, _ in g1 + g2]))
    val1 = [generi1.get(k, 0) for k in labels]
    val2 = [generi2.get(k, 0) for k in labels]
    x = np.arange(len(labels))
    width = 0.35

    plt.bar(x - width/2, val1, width, label=nome1, color='purple')
    plt.bar(x + width/2, val2, width, label=nome2, color='orange')
    plt.xticks(x, labels, rotation=45)
    plt.ylabel("Occorrenze")
    plt.title("Generi Musicali a Confronto")
    plt.legend()
    grafico_generi = salva_grafico()

    return {
        "nome1": nome1,
        "nome2": nome2,
        "num_comuni": len(brani_comuni),
        "artisti_comuni": len(artisti_comuni),
        "pop_avg_1": round(pop_avg_1, 2),
        "pop_avg_2": round(pop_avg_2, 2),
        "grafico_pop": grafico_pop,
        "grafico_anni": grafico_anni,
        "grafico_generi": grafico_generi
    }
