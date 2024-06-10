import pandas as pd
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime

#per qualche strano mottivo il codice funziona solo se eseguito con flask attivo
def add_data(file_path):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["mydatabase"]
    collezione = db["users"]

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

    collezione.insert_one({
            "nome": 'pippo',
            "cognome": 'franco',
            "data_di_nascita": datetime(2021, 7, 15),
            "username": 'franco',
            "password": 'franco',
            "film_visti": film_visti,
            "film_da_vedere": film_da_vedere,
        })
   


    



