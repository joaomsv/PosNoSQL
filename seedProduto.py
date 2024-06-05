from pymongo import MongoClient
from random import randrange
from faker import Faker

fake = Faker('pt_BR')
db = 'loja'
col = 'estoque'
filiais = 100000
# Tamanho do batch de docs que deseja ter
size = 100000
# Quantos batches deseja
batch = 5
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
        mydocs.append({
            '_id': (size * j) + i + 1,
            'produto': f'produto {i + 1}',
            'valor': randrange(1, 100),
            'qtd': randrange(100),
            'filial_id': randrange(filiais) + 1,
            'shard_key': randrange(round(size/5)) + 1})
    print(f'Seeding Produtos batch {j + 1}...')
    x = mycol.insert_many(mydocs)
    mydocs.clear()

# Define o shard key
mycol.create_index({'shard_key': 'hashed'})
client['admin'].command({'shardCollection': 'loja.estoque', 'key': {'shard_key': 'hashed'}})

client.close()
print(f'Quantidade de produtos: {max(x.inserted_ids)}')
print('Seeding Completed!!!')
