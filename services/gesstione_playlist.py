import pandas as pd
import plotly.express as px
from services.spotify_api import get_playlist_details  

def analyze_and_visualize(playlist_id):
   
    tracks = get_playlist_details(playlist_id)

    if not tracks:
        print("Nessun dato disponibile per l'analisi.")
        return None

    
    data = [
        {
            "artist": track["artist"],
            "album": track["album"],
            "track_name": track["name"],
            "popularity": track.get("popularity", 0),
            "genre": track.get("genre", "Sconosciuto") 
        }
        for track in tracks
    ]

    df = pd.DataFrame(data)

    if df.empty:
        print("DataFrame vuoto, impossibile generare il grafico.")
        return None

   
    top_artists = df.groupby("artist")["popularity"].sum().nlargest(5).reset_index()
    fig_artists = px.bar(top_artists, x="artist", y="popularity", title="Top 5 Artisti più popolari")

    
    top_albums = df.groupby("album")["popularity"].sum().nlargest(5).reset_index()
    fig_albums = px.bar(top_albums, x="album", y="popularity", title="Top 5 Album più popolari")

    
    genre_counts = df["genre"].str.split(", ", expand=True).stack().value_counts().reset_index()
    genre_counts.columns = ["genre", "count"]

   
    genre_counts = genre_counts[genre_counts["genre"] != "Sconosciuto"]

    
    fig_genres = px.pie(
        genre_counts,
        names="genre",
        values="count",
        title="Distribuzione dei Generi Musicali",
        labels={"genre": "Genere", "count": "Numero di brani"}
    )

    
    return {
        "fig_artists": fig_artists.to_html(full_html=False),
        "fig_albums": fig_albums.to_html(full_html=False),
        "fig_genres": fig_genres.to_html(full_html=False),
    }