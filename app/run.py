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


# Endpoint per ottenere un film per titolo o sottostringa del titolo
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


# ricerca film per id
@app.route("/movie/<movie_id>")
def movie_detail(movie_id):
    movie = movie_collection.find_one({"_id": ObjectId(movie_id)})
    return render_template("movie_detail.html", movie=movie)


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
@app.route("/reg", methods=["POST"])
def reg_user():
    nm = request.form['name']
    sr = request.form['surname']
    br = request.form['birthday']
    un = request.form['uname']
    pas = request.form['psw']
    documento= user_collection.find_one({"username": un})
    if documento: 
        return render_template("reg.html", errors="usr")
    else:
        user_collection.insert_one({
            "nome": nm,
            "cognome": sr,
            "data_di_nascita": br,
            "username": un,
            "password": pas,
            "film_visti": "NaN",
            "film_da_vedere": "NaN",
         })
        print('cesi')
    usrs=user_collection.find()       
    for el in usrs:
        print(el)
    movies = list(movie_collection.aggregate([{"$sample": {"size": 45}}]))
    return render_template("reg.html", movies=movies)


@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for("homepage"))


@app.route("/user")
def printUser():
    user = session.get("user")
    print(user)
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
    return jsonify({"redirect_url": url_for("homepage")})


@app.route("/add_to_favorites/<movie_id>", methods=["POST"])
def add_to_favorites(movie_id):
    if "user" not in session:
        return jsonify({"error": "Utente non autenticato"}), 401  # Unauthorized
    user = session["user"]
    user_data = user_collection.find_one({"_id": ObjectId(user["_id"])})
    if movie_id in user_data.get("favourites", []):
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])}, {"$pull": {"favourites": movie_id}}
        )
    else:
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])}, {"$addToSet": {"favourites": movie_id}}
        )

    updated_user = user_collection.find_one({"_id": ObjectId(user["_id"])})
    updated_user["_id"] = str(updated_user["_id"])

    session["user"] = updated_user
    return jsonify({"message": "Preferiti aggiornati con successo"}), 200  # OK


@app.route("/add_to_watchlist/<movie_id>", methods=["POST"])
def add_to_watchlist(movie_id):
    if "user" not in session:
        return jsonify({"error": "Utente non autenticato"}), 401  # Unauthorized
    user = session["user"]
    data = request.get_json()
    date = data.get("date")
    user_data = user_collection.find_one({"_id": ObjectId(user["_id"])})
    if movie_id in user_data.get("watchlist", []):
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$pull": {"watchlist": {"movie_id": movie_id}}},
        )
    else:
        user_collection.update_one(
            {"_id": ObjectId(user["_id"])},
            {"$addToSet": {"watchlist": {"movie_id": movie_id, "date": date}}},
        )
    updated_user = user_collection.find_one({"_id": ObjectId(user["_id"])})
    updated_user["_id"] = str(updated_user["_id"])

    session["user"] = updated_user
    return jsonify({"message": "Watchlist aggiornata con successo"}), 200  # OK


if __name__ == "__main__":
    app.run(debug=True)
