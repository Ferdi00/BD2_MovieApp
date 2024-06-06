from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import re, sys


app = Flask(__name__)

# Imposta l'encoding a UTF-8 per la console
sys.stdout.reconfigure(encoding="utf-8")

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

    return jsonify(movies)


# ricerca film per id
@app.route("/movie/<movie_id>")
def movie_detail(movie_id):
    movie = collection.find_one({"_id": ObjectId(movie_id)})
    return render_template("movie_detail.html", movie=movie)


@app.route("/api/filter", methods=["GET"])
def filter_movies():
    genres = request.args.getlist("genre")
    rating = request.args.get("rating", "")
    min_duration = request.args.get("min_duration", "")
    max_duration = request.args.get("max_duration", "")
    filter_criteria = {}

    if genres:
        # Costruisci una regex per cercare qualsiasi genere specificato
        regex_pattern = "|".join([re.escape(genre) for genre in genres])
        filter_criteria["genre"] = {"$regex": regex_pattern, "$options": "i"}
    if rating:
        filter_criteria["rating"] = {"$gte": float(rating)}
    if min_duration:
        filter_criteria["duration"] = {"$gte": int(min_duration)}
    if max_duration:
        if "duration" in filter_criteria:
            filter_criteria["duration"]["$lte"] = int(max_duration)
        else:
            filter_criteria["duration"] = {"$lte": int(max_duration)}

    movies = list(collection.find(filter_criteria))
    for movie in movies:
        movie["_id"] = str(movie["_id"])

    return jsonify(movies)


# homepage
@app.route("/")
def homepage():
    movies = list(collection.aggregate([{"$sample": {"size": 45}}]))
    return render_template("index.html", movies=movies)


if __name__ == "__main__":
    app.run(debug=True)
