import logging
from datetime import datetime

import pandas as pd
from pymongo import MongoClient

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_data(file_path):
    try:
        logging.info("Inizio del caricamento dei dati.")

        data = pd.read_csv(file_path)
        logging.info("Dati letti dal file CSV.")

        client = MongoClient("mongodb://localhost:27017/")
        db = client["mydatabase"]
        collezione_utenti = db["users"]

        # Cancella la collezione movies se esiste già
        db.drop_collection("movies")
        logging.info("Collezione 'movies' eliminata (se esisteva).")

        # Sostituisci i valori NaN con "NaN"
        data = data.fillna("NaN")

        for index, row in data.iterrows():
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
            if index % 100 == 0:  # Mostra un messaggio ogni 100 inserimenti
                logging.info(f"{index} film inseriti nella collezione 'movies'.")

        db.drop_collection("users")
        logging.info("Collezione 'users' eliminata (se esisteva).")

        collezione_utenti.insert_one(
            {
                "name": "Ferdinando",
                "surname": "Boccia",
                "birthday": "2024-06-01",
                "username": "Ferdi",
                "password": "Ferdi",
                "watchlist": [],
                "favorites": [],
            }
        )
        logging.info("Dati utente inseriti nella collezione 'users'.")

        logging.info("Caricamento dei dati completato con successo.")

    except Exception as e:
        logging.error(f"Errore durante il caricamento dei dati: {e}")


if __name__ == "__main__":
    load_data("dataset/movies.csv")
