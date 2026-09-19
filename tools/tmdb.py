import requests

from config import TMDB_API_KEY


def search_movie(movie_name):

    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_name
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        movies = []

        for movie in data.get("results", [])[:5]:
            movies.append({
                "id": movie.get("id"),
                "title": movie.get("title"),
                "release_date": movie.get("release_date"),
                "rating": movie.get("vote_average"),
                "overview": movie.get("overview")
            })

        return movies

    except requests.exceptions.RequestException as error:
        return {
            "error": True,
            "message": str(error)
        }