from pymongo import MongoClient
from random import randrange

db = 'loja'
col = 'estoque'
filiais = 3
# Tamanho do batch de docs que deseja ter
size = 500000
# Quantos batches deseja
batch = 3
MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)

# Define o tamanho dos chunks
client['config']['settings'].update_one({ '_id': "chunksize" }, { '$set': { '_id': "chunksize", 'value': 5 } }, upsert=True)

mydb = client[db]
mycol = mydb[col]
mydocs = []

# Sempre começar com uma coleção novo
if mycol.count_documents({}):
    mycol.drop()

for j in range(batch):
    for i in range(size):
        mydocs.append({'_id': (size * j) + i + 1, 'produto': f'produto {i + 1}', 'valor': randrange(100), 'qtd': randrange(100), 'filial': randrange(filiais) + 1, 'shard_key': randrange(round(size/5)) + 1})
    x = mycol.insert_many(mydocs)
    mydocs.clear()

# Define o shard key
mycol.create_index({'shard_key': 'hashed'})
client['admin'].command({'shardCollection': 'loja.estoque', 'key': {'shard_key': 'hashed'}})

print(max(x.inserted_ids))
client.close()
