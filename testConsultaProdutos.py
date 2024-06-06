from pymongo import MongoClient
from random import randrange

MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)
mydb = client['loja']
filiais = mydb['filial'].count_documents({})

print('Test beginning...')

for _ in range(1000):
    x = mydb['estoque'].count_documents({'filial': randrange(filiais) + 1, 'valor': {'$gte': randrange(100)}})

print('Test end!!!')
client.close()
