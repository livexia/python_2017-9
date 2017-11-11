# -*- coding: UTF-8 -*-
from pymongo import MongoClient

def insert_into_mongdb(database, col, data):
    client = MongoClient('localhost',27018)
    db = client.get_database(database)
    collection = db.get_collection(col)
    try:
        col_id = collection.save(data)
        print(col_id)
    except Exception as e:
        print(r'Insert into mongodb error: ', e)
    finally:
        return 0