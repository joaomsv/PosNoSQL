from pymongo import MongoClient
from random import randrange
from faker import Faker

fake = Faker('pt_BR')
MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)
mydb = client['loja']
filiais = mydb['filial'].count_documents({})
new_filial = mydb['filial'].count_documents({}) + 1000
mydocs = []

print('Test beginning...')

for i in range(filiais, new_filial):
    mydocs.append({'_id': i + 1,
                   'nome': fake.company(),
                   'endereço': fake.address(),
                   'gerente': fake.name(),
                   'shard_key': i})
mydb['produto'].insert_many(mydocs)
mydocs.clear()

print('Test end!!!')
client.close()
