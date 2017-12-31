from pyspider.result import ResultWorker
from pymongo import MongoClient

class MyResultWorker(ResultWorker):
    def on_result(self, task, result):
        assert task['taskid']
        assert task['project']
        assert task['url']
        assert result
        insert_into_mongdb('pyspider', task['project'], result)
    
def insert_into_mongdb(database, col, data):
    client = MongoClient('localhost',27018)
    db = client.get_database(database)
    collection = db.get_collection(col)
    try:
        col_id = collection.save(data)
        print('Insert success _id = {}'.format(col_id))
    except Exception as e:
        print('Insert into mongodb error: {}'.format(e))
        #exit(0)