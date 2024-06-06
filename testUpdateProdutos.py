from pymongo import MongoClient
from random import randrange

MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)
mydb = client['loja']
# mydocs = []
produtos = mydb['produto'].count_documents({})

print('Test beginning...')

for i in range(1000):
    # mydocs.append({ '_id': produtos + 1 },
    #               {'$set': {'qtd': randrange(100)}})
    mydb['produto'].update_one({ '_id': produtos + 1 },
                  {'$set': {'qtd': randrange(1000)}})
# mydocs.clear()

print('Test end!!!')
client.close()
