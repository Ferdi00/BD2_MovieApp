import pandas as pd
from pymongo import MongoClient


def load_data(file_path):
    data = pd.read_csv(file_path)
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]

    # Cancella la collezione movies se esiste già
    db.drop_collection("movies")

    # Sostituisci i valori NaN con "NaN"
    data = data.fillna("NaN")

    for _, row in data.iterrows():
        movie = {
            "poster": row["Poster"],
            "title": row["Title"],
            "year": row["Year"],
            "certificate": row["Certificate"],
            "duration": row["Duration (min)"],
            "genre": row["Genre"],
            "rating": row["Rating"],
            "metascore": row["Metascore"],
            "director": row["Director"],
            "cast": row["Cast"],
            "votes": row["Votes"],
            "description": row["Description"],
            "review_count": row["Review Count"],
            "review_title": row["Review Title"],
            "review": row["Review"],
        }
        db.movies.insert_one(movie)


if __name__ == "__main__":
    load_data("dataset/movies.csv")
