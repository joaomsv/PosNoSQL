from pymongo import MongoClient
from random import randrange
from faker import Faker

fake = Faker('pt_BR')
db = 'loja'
col = 'filial'
filiais = 100000
MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)

# Define o tamanho dos chunks
client['config']['settings'].update_one({ '_id': "chunksize" }, { '$set': { '_id': "chunksize", 'value': 5 } }, upsert=True)

mydb = client[db]
mycol = mydb[col]
mydocs = []

if mycol.count_documents({}):
    mycol.drop()

client['admin'].command({'shardCollection': 'loja.filial', 'key': {'shard_key': 1}})
for a in range(filiais):
    mydocs.append({'_id': a + 1,
                   'nome': fake.company(),
                   'endereço': fake.address(),
                   'gerente': fake.name(),
                   'shard_key': a})
print('Seeding Filiais...')
x = mycol.insert_many(mydocs)
mydocs.clear()

client.close()
print(f'Quantidade de filiais: {max(x.inserted_ids)}')
print('Seeding Completed!!!')
