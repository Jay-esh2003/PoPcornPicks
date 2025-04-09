# app.py
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model
import os
import pandas as pd

import requests

from dotenv import load_dotenv
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")  #environment variable

def get_poster_url(movie_title):
    import re

    # Remove year in parentheses, e.g., "Toy Story (1995)" → "Toy Story"
    cleaned_title = re.sub(r"\s*\(\d{4}\)", "", movie_title).strip()

    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": cleaned_title
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = data.get("results")
        if results and results[0].get("poster_path"):
            return f"https://image.tmdb.org/t/p/w500{results[0]['poster_path']}"
    except Exception as e:
        print(f"Poster fetch failed for {movie_title}: {e}")
    return None

def load_movies(path='ml-100k/u.item'):
    columns = ['movie_id', 'title', 'release_date', 'video_release_date',
               'imdb_url', 'unknown', 'Action', 'Adventure', 'Animation',
               'Children', 'Comedy', 'Crime', 'Documentary', 'Drama',
               'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery',
               'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    movies = pd.read_csv(path, sep='|', names=columns, encoding='latin-1')
    return dict(zip(movies['movie_id'], movies['title']))

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Load model and mappings
model = load_model("model/recommendation_model.keras")
movie_to_index = np.load("model/movie_to_index.npy", allow_pickle=True).item()
index_to_movie = {v: k for k, v in movie_to_index.items()}

movie_id_to_title = load_movies()

# Get movie embeddings from the model
movie_embedding_layer = model.get_layer('movie_embedding')
movie_embeddings = movie_embedding_layer.get_weights()[0]  # Shape: (num_movies, embedding_dim)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/movies')
def get_movies():
    movie_list = [
        {'id': movie_id, 'title': movie_id_to_title[movie_id]}
        for movie_id in movie_to_index.keys()
        if movie_id in movie_id_to_title
    ]
    return jsonify(movie_list)

@app.route('/recommend_by_movies', methods=['POST'])
def recommend_by_movies():
    data = request.get_json()
    selected_movie_ids = data.get('movie_ids', [])

    if not selected_movie_ids:
        return jsonify({'error': 'No movie IDs provided'}), 400

    # Convert to indices
    selected_indices = [movie_to_index[movie] for movie in selected_movie_ids if movie in movie_to_index]

    if not selected_indices:
        return jsonify({'error': 'No valid movie indices found'}), 400

    # Get embeddings and compute average
    selected_embeddings = movie_embeddings[selected_indices]
    average_embedding = np.mean(selected_embeddings, axis=0)

    # Compute cosine similarity
    norms = np.linalg.norm(movie_embeddings, axis=1)
    avg_norm = np.linalg.norm(average_embedding)
    similarities = movie_embeddings @ average_embedding / (norms * avg_norm + 1e-10)

    # Get top N recommendations
    top_indices = np.argsort(similarities)[::-1]
    top_indices = [i for i in top_indices if i not in selected_indices][:10]

    # Map internal indices → real movie IDs → movie titles
    recommended_movies = []
    for i in top_indices:
        movie_id = index_to_movie[i]
        if movie_id in movie_id_to_title:
            title = movie_id_to_title[movie_id]
            poster_url = get_poster_url(title)  # <-- fetch poster using TMDB
            recommended_movies.append({
                "title": title,
                "poster": poster_url
            })

    return jsonify({'recommendations': recommended_movies})

if __name__ == '__main__':
    app.run(debug=True)
