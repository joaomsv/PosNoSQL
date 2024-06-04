from pymongo import MongoClient
from random import randrange

db = 'loja'
col_estoque = 'estoque'
col_filial = 'filial'
filiais = 500000
# Tamanho do batch de docs que deseja ter
size = 500000
# Quantos batches deseja
batch = 1
MONGODB_URI = 'mongodb://localhost:27017/'
client = MongoClient(MONGODB_URI)

# Define o tamanho dos chunks
client['config']['settings'].update_one({ '_id': "chunksize" }, { '$set': { '_id': "chunksize", 'value': 5 } }, upsert=True)

mydb = client[db]
mycol_es = mydb[col_estoque]
mycol_fi = mydb[col_filial]
mydocs = []

# Sempre começar com uma coleção novo
if mycol_es.count_documents({}):
    mycol_es.drop()

if mycol_fi.count_documents({}):
    mycol_fi.drop()

client['admin'].command({'shardCollection': 'loja.filial', 'key': {'shard_key': 1}})
for a in range(filiais):
    mydocs.append({'_id': a + 1, 'nome': f'loja{a + 1}', 'shard_key': a})
x = mycol_fi.insert_many(mydocs)
mydocs.clear()
print(max(x.inserted_ids))

for j in range(batch):
    for i in range(size):
        mydocs.append({'_id': (size * j) + i + 1, 'produto': f'produto {i + 1}', 'valor': randrange(100), 'qtd': randrange(100), 'filial': randrange(filiais) + 1, 'shard_key': randrange(round(size/5)) + 1})
    x = mycol_es.insert_many(mydocs)
    mydocs.clear()

# Define o shard key
mycol_es.create_index({'shard_key': 'hashed'})
client['admin'].command({'shardCollection': 'loja.estoque', 'key': {'shard_key': 'hashed'}})

print(max(x.inserted_ids))
client.close()
