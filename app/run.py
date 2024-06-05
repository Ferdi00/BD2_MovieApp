from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import re


app = Flask(__name__)

# Configurazione del client MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["movies"]


# Endpoint per mostrare le collezioni nel database
@app.route("/showcollections")
def show_collections():
    collections = db.list_collection_names()
    return jsonify(collections)


# Endpoint per ottenere tutti i film
@app.route("/movies", methods=["GET"])
def get_movies():
    movies = list(db.movies.find({}, {"_id": 0}))
    return jsonify(movies)


# Endpoint per ottenere un film per titolo o sottostringa del titolo
@app.route("/search", methods=["GET"])
def search_movies():
    query = request.args.get("query", "")
    # Esegui la ricerca nel database utilizzando una regex per trovare tutte le occorrenze della sottostringa nel titolo
    movies = list(
        collection.find(
            {"title": {"$regex": f".*{re.escape(query)}.*", "$options": "i"}}
        )
    )

    # Converte gli _id in stringhe prima di restituire la risposta JSON
    for movie in movies:
        movie["_id"] = str(movie["_id"])

    print(movies)

    return jsonify(movies)


# ricerca film per id
@app.route("/movie/<movie_id>")
def movie_detail(movie_id):
    movie = collection.find_one({"_id": ObjectId(movie_id)})
    return render_template("movie_detail.html", movie=movie)


# Endpoint per ottenere film per genere
@app.route("/movies/genre/<genre>", methods=["GET"])
def get_movies_by_genre(genre):
    movies = list(db.movies.find({"genre": genre}, {"_id": 0}))
    if movies:
        return jsonify(movies)
    else:
        return jsonify({"error": "No movies found for this genre"}), 404


# homepage
@app.route("/")
def homepage():
    movies = list(collection.aggregate([{"$sample": {"size": 48}}]))
    return render_template("index.html", movies=movies)


if __name__ == "__main__":
    app.run(debug=True)
