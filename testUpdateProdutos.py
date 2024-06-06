from pymongo import MongoClient
from random import randrange

MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)
mydb = client['loja']
produtos = mydb['estoque'].count_documents({})

print('Test beginning...')

for i in range(1000):
    mydb['estoque'].update_one({ '_id': produtos + 1 },
                  {'$set': {'qtd': randrange(1000)}})

print('Test end!!!')
client.close()
