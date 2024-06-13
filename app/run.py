from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import re, sys
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Imposta l'encoding a UTF-8 per la console
sys.stdout.reconfigure(encoding="utf-8")

# Configurazione del client MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
movie_collection = db["movies"]
user_collection = db["users"]


def get_unique_genres():
    pipeline = [{"$unwind": "$genre"}, {"$group": {"_id": "$genre"}}]
    results = movie_collection.aggregate(pipeline)

    unique_genres = set()
    for result in results:
        genres = [genre.strip() for genre in result["_id"].split(",")]
        unique_genres.update(genres)

homepage_movies = list(movie_collection.aggregate([{"$sample": {"size": 45}}]))

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


# Endpoint per ottenere username film per titolo o sottostringa del titolo
@app.route("/search", methods=["GET"])
def search_movies():
    query = request.args.get("query", "")
    # Esegui la ricerca nel database utilizzando una regex per trovare tutte le occorrenze della sottostringa nel titolo
    movies = list(
        movie_collection.find(
            {"title": {"$regex": f".*{re.escape(query)}.*", "$options": "i"}}
        )
    )

    # Converte gli _id in stringhe prima di restituire la risposta JSON
    for movie in movies:
        movie["_id"] = str(movie["_id"])

    return jsonify(movies)


@app.route("/movie/<movie_id>")
def movie_detail(movie_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))

    movie = movie_collection.find_one({"_id": ObjectId(movie_id)})
    if not movie:
        return "Movie not found", 404

    user_data = user_collection.find_one({"_id": ObjectId(user["_id"])})
    favorites = movie_id in user_data.get("favorites", [])
    watchlist = any(
        item["movie_id"] == movie_id for item in user_data.get("watchlist", [])
    )
    score = user_data.get("user_scores", {}).get(movie_id)

    return render_template(
        "movie_detail.html",
        movie=movie,
        favorites=favorites,
        watchlist=watchlist,
        score=score,
        user=user,
    )


@app.route("/api/filter", methods=["GET"])
def filter_movies():
    genres = request.args.getlist("genre")
    rating = request.args.get("rating", "")
    min_duration = request.args.get("min_duration", "")
    max_duration = request.args.get("max_duration", "")
    min_year = request.args.get("min_year", "")
    max_year = request.args.get("max_year", "")
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
    if min_year:
        filter_criteria["year"] = {"$gte": int(min_year)}
    if max_year:
        if "year" in filter_criteria:
            filter_criteria["year"]["$lte"] = int(max_year)
        else:
            filter_criteria["year"] = {"$lte": int(max_year)}

    movies = list(movie_collection.find(filter_criteria))
    for movie in movies:
        movie["_id"] = str(movie["_id"])

    return jsonify(movies)


# homepage
@app.route("/")
def homepage():
    user = session.get("user")
    return render_template("index.html", movies=homepage_movies, user=user)

# login page
@app.route("/login")
def login():
    return render_template("login.html")

# POST login
@app.route("/login", methods=["POST"])
def login_user():
    username = request.form["uname"]
    password = request.form["psw"]
    user = user_collection.find_one({"username": username, "password": password})
    if user:
        user["_id"] = str(user["_id"])
        session['user'] = user
        return redirect(url_for("homepage"))
    else:
        return redirect(url_for('login'))

# reg
@app.route("/signin", methods=["GET"])
def reg():
    return render_template("signin.html")


# Endpoint per registrare l'utente
@app.route("/signin", methods=["POST"])
def reg_user():
    name = request.form['name']
    surname = request.form['surname']
    birthday = request.form['birthday']
    username = request.form['uname']
    password = request.form['psw']
    user = user_collection.find_one({"username": username})
    if user: 
        return render_template("signin.html", errors="usr")
    else:
        user_collection.insert_one(
            {
                "name": name,
                "surname": surname,
                "birthday": birthday,
                "username": username,
                "password": password,
                "watchlist": [],
                "favorites": [],
            }
        )
        user = user_collection.find_one({"username": username, "password": password})
        user["_id"] = str(user["_id"])
        session["user"] = user
    return redirect(url_for("homepage"))

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("homepage"))


@app.route("/user")
def printUser():
    user = session.get("user")
    return jsonify(user)


@app.route("/user_score/<movie_id>", methods=["POST"])
def add_user_score(movie_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "You need to log in first."}), 401

    data = request.get_json()
    score = data.get("score")
    if not score:
        return jsonify({"error": "Score is required"}), 400

    user_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {f"user_scores.{movie_id}": float(score)}}
    )

    updated_user = user_collection.find_one({"_id": ObjectId(user["_id"])})
    updated_user["_id"] = str(updated_user["_id"])

    session["user"] = updated_user
    message = "User score added/modified successfully"
    return jsonify({"message": message}), 200  # OK


@app.route("/add_to_favorites/<movie_id>", methods=["POST"])
def add_to_favorites(movie_id):
    user = session.get("user")

    if not user:
        return jsonify({"error": "You need to log in first."}), 401
    user_data = user_collection.find_one({"_id": ObjectId(user["_id"])})
    if movie_id in user_data.get("favorites", []):
        # Remove the movie from favorites if it is already there
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])}, {"$pull": {"favorites": movie_id}}
        )
        message = "Movie removed from favorites successfully"
    else:
        # Add the movie to favorites if it is not there
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])}, {"$addToSet": {"favorites": movie_id}}
        )
        message = "Movie added to favorites successfully"

    updated_user = user_collection.find_one({"_id": ObjectId(user["_id"])})
    updated_user["_id"] = str(updated_user["_id"])

    session["user"] = updated_user
    return jsonify({"message": message}), 200  # OK


@app.route("/add_to_watchlist/<movie_id>", methods=["POST"])
def add_to_watchlist(movie_id):
    user = session.get("user")
    if not user:
        return jsonify({"error": "You need to log in first."}), 401
    data = request.get_json()
    date = data.get("seenDate")
    user_data = user_collection.find_one({"_id": ObjectId(user["_id"])})
    # Check if the movie is already in the watchlist
    watchlist = user_data.get("watchlist", [])
    if any(movie.get("movie_id") == movie_id for movie in watchlist):
        user_collection.update_one(
                {"_id": ObjectId(user["_id"])},
                {"$pull": {"watchlist": {"movie_id": movie_id}}},
            )
        message = "Movie removed from watchlist successfully"
    else:
        # Add movie to the watchlist
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$addToSet": {"watchlist": {"movie_id": movie_id, "date": date}}},
        )
        message = "Movie added to watchlist successfully"
   
    updated_user = user_collection.find_one({"_id": ObjectId(user["_id"])})
    updated_user["_id"] = str(updated_user["_id"])

    session["user"] = updated_user
    return jsonify({"message": message}), 200  # OK

@app.route("/personal_area")
def personal_area():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    
    #if there are favorites in the user I extract them from the film collection
    if user.get("favorites"):
      favorites = []
      for film_id in user.get("favorites"):
         film = movie_collection.find_one({"_id": ObjectId(film_id)})
         film["_id"] = str(film["_id"])
         favorites.append(movie_collection.find_one({"_id": ObjectId(film_id)}))
         print(favorites)
    else:
        favorites="NaN"

    #if there are watchlistfilm in the user I extract them from the film collection
    if user.get("watchlist"):
      watchlist = []
      for film_id in user.get("watchlist"):
         film = movie_collection.find_one({"_id": ObjectId(film_id)})
         film["_id"] = str(film["_id"])
         watchlist.append(movie_collection.find_one({"_id": ObjectId(film_id)}))
         print(watchlist)
    else:
        watchlist="NaN"

    return render_template(
        "personal_area.html",
        favorites=favorites,
        watchlist=watchlist,
        user=user,
    )

if __name__ == "__main__":
    app.run(debug=True)
