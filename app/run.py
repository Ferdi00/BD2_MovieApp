from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from bson.objectid import ObjectId
import re, sys
from datetime import datetime



app = Flask(__name__)

# Imposta l'encoding a UTF-8 per la console
sys.stdout.reconfigure(encoding="utf-8")

# Configurazione del client MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["movies"]
collection1 = db["users"]


def get_unique_genres():
    pipeline = [{"$unwind": "$genre"}, {"$group": {"_id": "$genre"}}]
    results = collection.aggregate(pipeline)

    unique_genres = set()
    for result in results:
        genres = [genre.strip() for genre in result["_id"].split(",")]
        unique_genres.update(genres)


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

    movies = list(collection.find(filter_criteria))
    for movie in movies:
        movie["_id"] = str(movie["_id"])

    return jsonify(movies)


# homepage
@app.route("/")
def homepage():
    movies = list(collection.aggregate([{"$sample": {"size": 45}}]))
    '''
    # parte per inserire i dati di un utente
    
     # Esempio di dati da inserire
    film_visti = [
    {"nome": "Inception", "data_di_visione": datetime(2021, 5, 21)},
    {"nome": "The Matrix", "data_di_visione": datetime(2021, 6, 10)},
    {"nome": "Interstellar", "data_di_visione": datetime(2021, 7, 15)}
    ]

    film_da_vedere = [
    {"nome": "Inception"},
    {"nome": "The Matrix"},
    {"nome": "Interstellar"}
    ]
    collezione = db["users"]
    collezione.insert_one({
            "nome": 'pippo',
            "cognome": 'franco',
            "data_di_nascita": datetime(2021, 7, 15),
            "username": 'franco',
            "password": 'franco',
            "film_visti": film_visti,
            "film_da_vedere": film_da_vedere,
        })
    #fine inserimento 
    
    # parte per inserire i dati di un utente
    
     # Esempio di dati da inserire
     
    film_visti = [
    {"nome": "My Spy", "data_di_visione": datetime(2021, 5, 21)},
    {"nome": "The Incredibles", "data_di_visione": datetime(2021, 6, 10)},
    ]

    film_da_vedere = [
    {"nome": "Foxcatcher"},
    {"nome": "Sacrifice"},
    ]
    collezione = db["users"]
    collezione.insert_one({
            "nome": 'pippo',
            "cognome": 'franco',
            "data_di_nascita": datetime(2021, 7, 15),
            "username": 'fra',
            "password": 'franco',
            "film_visti": film_visti,
            "film_da_vedere": film_da_vedere,
        })
    #fine inserimento 
    
    for it in collezione.find():
        print(it)
    '''
    return render_template("index.html", movies=movies)

# login
@app.route("/login")
def login():
    movies = list(collection.aggregate([{"$sample": {"size": 45}}]))
    return render_template("login.html", movies=movies)

# Endpoint per verificare l'utente
@app.route("/login", methods=["POST"])
def login_user():
     un = request.form['uname']
     pas = request.form['psw']
     documento= collection1.find_one({"username": un,"password":pas})
     if documento: 
         print('bravo_cesi')
         preferiti=list()
         vis=list()
         for chiave,valore in documento.items():
          if chiave == 'film_da_vedere':
               for it in valore:
                if it != 'NaN':
                  print(it)
                  tit=it.get('nome')
                  print(tit)
                  iter=collection.find_one({"title": tit})
                  preferiti.append(iter)
                  print(iter)
          if chiave == 'film_visti':
               for it in valore:
                if it != 'NaN':
                  print(it)
                  tit=it.get('nome')
                  print(tit)
                  iter=collection.find_one({"title": tit})
                  vis.append(iter)
                  print(iter)
         return render_template("preferiti.html", pref=preferiti, visti=vis)
     else:
          print('sgamato')
          return render_template("login.html", errors="err")

# reg
@app.route("/reg", methods=["GET"])
def reg():
    movies = list(collection.aggregate([{"$sample": {"size": 45}}]))
    return render_template("reg.html", movies=movies)

# Endpoint per registrare l'utente
@app.route("/reg", methods=["POST"])
def reg_user():
     nm = request.form['name']
     sr = request.form['surname']
     br = request.form['birthday']
     un = request.form['uname']
     pas = request.form['psw']
     documento= collection1.find_one({"username": un})
     if documento: 
        print('sgamato')
        return render_template("reg.html", errors="usr")
     else:
            collection1.insert_one({
            "nome": nm,
            "cognome": sr,
            "data_di_nascita": br,
            "username": un,
            "password": pas,
            "film_visti": "NaN",
            "film_da_vedere": "NaN",
         })
            print('cesi')
     usrs=collection1.find()       
     for el in usrs:
         print(el)
     movies = list(collection.aggregate([{"$sample": {"size": 45}}]))
     return render_template("reg.html", movies=movies)
     
# homepage
@app.route("/preferiti")
def pref():
    movies = list(collection.find([{"$sample": {"size": 45}}]))
    return render_template("preferiti.html", movies=movies)

if __name__ == "__main__":
    app.run(debug=True)
