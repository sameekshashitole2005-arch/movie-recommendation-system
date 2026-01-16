import streamlit as st
import pandas as pd
import requests
import random

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(layout="wide")

# -------------------------------
# TMDB API KEY
# -------------------------------
API_KEY = "a088750352f3375e68d70e095568c7e4"

# -------------------------------
# NETFLIX STYLE CSS
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #141414;
}
.stApp {
    background-color: #141414;
}
h1, h2, h3 {
    color: white;
}
.hero {
    position: relative;
    height: 450px;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 30px;
}
.hero img {
    width: 100%;
}
.hero-text {
    position: absolute;
    bottom: 40px;
    left: 40px;
    color: white;
    max-width: 500px;
}
.hero-title {
    font-size: 48px;
    font-weight: bold;
}
.hero-info {
    font-size: 16px;
    color: #e5e5e5;
}
.movie-card-title {
    color: white;
    font-size: 14px;
    font-weight: bold;
}
.movie-card-info {
    color: #b3b3b3;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# LOAD MOVIES
# -------------------------------
movies = pd.read_csv("movies.csv")

# -------------------------------
# TMDB FUNCTIONS
# -------------------------------
def fetch_movie(movie_name):
    url = "https://api.themoviedb.org/3/search/movie"
    response = requests.get(url, params={
        "api_key": API_KEY,
        "query": movie_name
    })
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        return None

    m = data["results"][0]

    poster = (
        f"https://image.tmdb.org/t/p/original{m['backdrop_path']}"
        if m.get("backdrop_path")
        else "https://via.placeholder.com/1280x720?text=No+Image"
    )

    poster_small = (
        f"https://image.tmdb.org/t/p/w500{m['poster_path']}"
        if m.get("poster_path")
        else "https://via.placeholder.com/300x450?text=No+Poster"
    )

    return {
        "title": m["title"],
        "overview": m.get("overview", ""),
        "rating": m.get("vote_average", "N/A"),
        "genre_ids": m.get("genre_ids", []),
        "banner": poster,
        "poster": poster_small
    }

def get_genres(ids):
    url = "https://api.themoviedb.org/3/genre/movie/list"
    g = requests.get(url, params={"api_key": API_KEY}).json()
    genre_map = {x["id"]: x["name"] for x in g["genres"]}
    return ", ".join([genre_map.get(i, "") for i in ids])

# -------------------------------
# HERO MOVIE
# -------------------------------
featured_title = random.choice(movies["title"].tolist())
featured = fetch_movie(featured_title)

if featured:
    st.markdown(f"""
    <div class="hero">
        <img src="{featured['banner']}">
        <div class="hero-text">
            <div class="hero-title">{featured['title']}</div>
            <div class="hero-info">
                ⭐ {featured['rating']}<br>
                {featured['overview'][:200]}...
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# RECOMMENDER
# -------------------------------
st.markdown("## 🎬 Movie Recommender")

selected_movie = st.selectbox(
    "Select a movie you like",
    movies["title"].values
)

if st.button("Recommend"):
    st.markdown("## Recommended For You")

    recs = movies[movies["title"] != selected_movie]["title"].sample(8).tolist()
    cols = st.columns(8)

    for i, movie in enumerate(recs):
        m = fetch_movie(movie)
        if not m:
            continue

        genres = get_genres(m["genre_ids"])

        with cols[i]:
            st.image(m["poster"], use_container_width=True)
            st.markdown(f"<div class='movie-card-title'>{m['title']}</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='movie-card-info'>⭐ {m['rating']}<br>🎭 {genres}</div>",
                unsafe_allow_html=True
            )
