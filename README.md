# Atividade Final

## Cluster em MongoDB para Gerenciamento de Estoque

### Caso

Imagine que você está projetando um sistema de gerenciamento de estoque para uma cadeia de supermercados que possui filiais em diferentes cidades.

#### Requisitos

- Cada filial possui um grande volume de produtos em seu estoque.
- O sistema precisa ser capaz de lidar com milhões de registros de produtos.
- A consulta de estoque e atualizações de inventário devem ser rápidas e eficientes.
- A escalabilidade do sistema é essencial, pois novas filiais podem se adicionadas no futuro.

### Arquitetura

Com base nos requisitos, podemos concluir que os aspectos do Teorema do CAP que temos que garantir são:

- Consistência: Ao consultar o banco os dados dos produtos em qualquer filial a qualquer momento os dados exibidos deverão ser os mesmos.
- Tolerância à Partição: O sistema deve funcionar mesmo se alguma falha ocorrer em qual nó do cluster.

Sendo assim, com a indicação do professor e os requisitos, MongoDB foi escolhido para este trabalho.

![Arquitura MongoDB Cluster](./imagens/arqMongoCluster.png 'Arquitura MongoDB Cluster')

Essa arquitetura foi baseado no artigo [Criando um cluster MongoDB com ReplicaSet e Sharding com Docker](https://gustavo-leitao.medium.com/criando-um-cluster-mongodb-com-replicaset-e-sharding-com-docker-9cb19d456b56)

O que precisamos saber são o seguinte:

#### Replica Set

Um agrupamento de serviços para garantir a replicação e segurança contra falhas dos bancos.

#### Router

O router é uma instância de `mongos` que será a interface entre o cliente e o cluster. Caso necessário, pode criar uma replica set para melhorar a segurança contra falha.

#### Shard

Um shard ou fragmento, é onde os dados são armazenados. Sendo que existem 3 shards na minha arquitetura os dados devem ser divididos em chunks ou pedaços e distribuído entre eles. Os shards são feitos de uma replica set de 3 instâncias de `mongod` onde 1 é o primário e o resto secundários. Caso o primário falhar um dos secundários devia assumir como o novo primário.

#### Config Server

O config server contém os metadados e as configurações do cluster. Uma replica set de 3 instâncias de `mongod`, caso o primário falhar um dos secundários assume como primário.

### Implementação

Para automatizar o processo de montagem do cluster foi utilizado docker compose. ***Isto será feito em Windows para qualquer outra SO precisa trocar `\` para `/` no `compose.yaml`***

#### Network Setup

Inicialmente precisamos criar uma rede para que todos os containers consigam se comunicar entre si.

```yaml
networks:
  mongoLojas:
    driver: bridge
```

Através disto a nossa rede `mongoLojas` foi criada.

#### Config Server Setup

![Config Server Setup Arquitetura](./imagens/arqConfigSrvSetup.png 'Config Server Setup Arquitetura')

Consigamos ver pela imagem que vamos precisar de 4 containers para criar um config server.

```yaml
mongo-config1:
    image: mongo
    container_name: config1
    networks:
      - mongoLojas
    command: ['mongod', '--configsvr', '--replSet', 'config-server', '--port', '27017']

  mongo-config2:
    image: mongo
    container_name: config2
    networks:
      - mongoLojas
    command: ['mongod', '--configsvr', '--replSet', 'config-server', '--port', '27017']

  mongo-config3:
    image: mongo
    container_name: config3
    networks:
      - mongoLojas
    command: ['mongod', '--configsvr', '--replSet', 'config-server', '--port', '27017']
```

Aqui criamos 3 containers usando a imagem `mongo` e colocamos eles na mesma rede `mongoLojas`. Assim que os containers foram iniciados, o comando `mongod --configsvr --replSet config-server --port 27017` será executado. Isto irá configurar a instância `mongod`.

- `--configsvr`: Uma flag para configurar como config server
- `--replSet config-server`: Coloca todos no mesmo replica set
- `--port 27017`: Define o port para 27017

```yaml
config-srv-setup:
    image: mongo
    container_name: config-srv-setup
    volumes:
      - .\scripts:/scripts
    depends_on:
      - mongo-config1
      - mongo-config2
      - mongo-config3
    networks:
      - mongoLojas
    restart: no
    entrypoint: ['bash', './scripts/start-configdb.sh']
```

Em sequência temos que criar um container para finalizar a inicialização do config server. Ele aguarda a inicialização de `mongo-config1,  mongo-config2, mongo-config3` e executa o script `start-configdb.sh`.

```bash
sleep 5
mongosh --host config1:27017 <<EOF
    load('./scripts/config-setup.js')
EOF
```

Ele espera 5 segundos para que os outros containers acabem de inicializar e executar o comando. Primeiramente vai acessar o `mongosh` do primeiro container `config1` com `mongosh --host config1:27017` e irá executar `config-setup.js`.

```js
rs.initiate(
   {
     _id: "config-server",
      configsvr: true,
      version: 1,
      members: [
         { _id: 0, host : "config1:27017", priority: 2},
         { _id: 1, host : "config2:27017", priority: 1},
         { _id: 2, host : "config3:27017", priority: 0}
      ]
   }
)
```

Neste script ele inicializa o replica set do config server definindo todos os membros e as prioridades para quem deve ser o primário, sendo quanto maior o número maior a chance de ser o primário.

#### Shard Setup

![Shard Setup Arquitetura](./imagens/arqShardsSetup.png 'Shard Setup Arquitetura')

Agora vamos criar os 3 shards que irão armazenar os dados. Precisamos configurar cada um individualmente mas, a configuração para cada é similar alterando somente os nomes e ports.

##### Shard1

```yaml
mongo-shard1a:
    image: mongo
    container_name: shard1a
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard1', '--port', '27018']

  mongo-shard1b:
    image: mongo
    container_name: shard1b
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard1', '--port', '27018']

  mongo-shard1c:
    image: mongo
    container_name: shard1c
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard1', '--port', '27018']
```

Aqui criamos 3 containers usando a imagem `mongo` e colocamos eles na mesma rede `mongoLojas`. Assim que os containers foram iniciados, o comando `mongod --shardsvr --replSet shard1 --port 27018` será executado. Isto irá configurar a instância `mongod`.

- `--shardsvr`: Uma flag para configurar como shard
- `--replSet shard1`: Coloca todos no mesmo replica set
- `--port 27018`: Define o port para 27018

```yaml
shard1-setup:
    image: mongo
    container_name: shard1-setup
    volumes:
      - .\scripts:/scripts
    depends_on:
      - mongo-shard1a
      - mongo-shard1b
      - mongo-shard1c
    networks:
      - mongoLojas
    restart: no
    entrypoint: ['bash', './scripts/start-shard1.sh']
```

Em sequência temos que criar um container para finalizar a inicialização do shard1. Precisamos colocar na mesma rede `mongoLojas` e mapear a pasta `script` para poder usar os scripts depois. Ele aguarda a inicialização de `mongo-shard1a,  mongo-shard1b, mongo-shard1c` e executa o script `start-shard1.sh`.

```bash
sleep 5
mongosh --host shard1a:27018 <<EOF
    load('./scripts/shard1-setup.js')
EOF
```

Ele espera 5 segundos para que os outros containers acabem de inicializar e executar o comando. Primeiramente vai acessar o `mongosh` do primeiro container `shard1a` com `mongosh --host shard1a:27018` e irá executar `shard1-setup.js`.

```js
rs.initiate(
    {
       _id: "shard1",
       version: 1,
       members: [
          { _id: 0, host : "shard1a:27018", priority: 2},
          { _id: 1, host : "shard1b:27018", priority: 1},
          { _id: 2, host : "shard1c:27018", priority: 0}
       ]
    }
)
```

Neste script ele inicializa o replica set do shard1 definindo todos os membros e as prioridades para quem deve ser o primário, sendo quanto maior o número maior a chance de ser o primário. Assim que ele finaliza a tarefa o container para.

##### Shard2

```yaml
mongo-shard2a:
    image: mongo
    container_name: shard2a
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard2', '--port', '27019']

  mongo-shard2b:
    image: mongo
    container_name: shard2b
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard2', '--port', '27019']

  mongo-shard2c:
    image: mongo
    container_name: shard2c
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard2', '--port', '27019']
```

Aqui criamos 3 containers usando a imagem `mongo` e colocamos eles na mesma rede `mongoLojas`. Assim que os containers foram iniciados, o comando `mongod --shardsvr --replSet shard2 --port 27019` será executado. Isto irá configurar a instância `mongod`.

- `--shardsvr`: Uma flag para configurar como shard
- `--replSet shard2`: Coloca todos no mesmo replica set
- `--port 27019`: Define o port para 27019

```yaml
shard2-setup:
    image: mongo
    container_name: shard2-setup
    volumes:
      - .\scripts:/scripts
    depends_on:
      - mongo-shard2a
      - mongo-shard2b
      - mongo-shard2c
    networks:
      - mongoLojas
    restart: no
    entrypoint: ['bash', './scripts/start-shard2.sh']
```

Em sequência temos que criar um container para finalizar a inicialização do shard2. Precisamos colocar na mesma rede `mongoLojas` e mapear a pasta `script` para poder usar os scripts depois. Ele aguarda a inicialização de `mongo-shard2a,  mongo-shard2b, mongo-shard2c` e executa o script `start-shard2.sh`.

```bash
sleep 5
mongosh --host shard2a:27019 <<EOF
    load('./scripts/shard2-setup.js')
EOF
```

Ele espera 5 segundos para que os outros containers acabem de inicializar e executar o comando. Primeiramente vai acessar o `mongosh` do primeiro container `shard2a` com `mongosh --host shard2a:27019` e irá executar `shard2-setup.js`.

```js
rs.initiate(
    {
       _id: "shard2",
       version: 1,
       members: [
          { _id: 0, host : "shard2a:27019", priority: 2},
          { _id: 1, host : "shard2b:27019", priority: 1},
          { _id: 2, host : "shard2c:27019", priority: 0}
       ]
    }
)
```

Neste script ele inicializa o replica set do shard2 definindo todos os membros e as prioridades para quem deve ser o primário, sendo quanto maior o número maior a chance de ser o primário. Assim que ele finaliza a tarefa o container para.

##### Shard3

```yaml
mongo-shard3a:
    image: mongo
    container_name: shard3a
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard3', '--port', '27020']

  mongo-shard3b:
    image: mongo
    container_name: shard3b
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard3', '--port', '27020']

  mongo-shard3c:
    image: mongo
    container_name: shard3c
    networks:
      - mongoLojas
    command: ['mongod', '--shardsvr', '--replSet', 'shard3', '--port', '27020']
```

Aqui criamos 3 containers usando a imagem `mongo` e colocamos eles na mesma rede `mongoLojas`. Assim que os containers foram iniciados, o comando `mongod --shardsvr --replSet shard3 --port 27020` será executado. Isto irá configurar a instância `mongod`.

- `--shardsvr`: Uma flag para configurar como shard
- `--replSet shard3`: Coloca todos no mesmo replica set
- `--port 27020`: Define o port para 27020

```yaml
shard3-setup:
    image: mongo
    container_name: shard3-setup
    volumes:
      - .\scripts:/scripts
    depends_on:
      - mongo-shard3a
      - mongo-shard3b
      - mongo-shard3c
    networks:
      - mongoLojas
    restart: no
    entrypoint: ['bash', './scripts/start-shard3.sh']
```

Em sequência temos que criar um container para finalizar a inicialização do shard3. Precisamos colocar na mesma rede `mongoLojas` e mapear a pasta `script` para poder usar os scripts depois. Ele aguarda a inicialização de `mongo-shard3a,  mongo-shard3b, mongo-shard3c` e executa o script `start-shard3.sh`.

```bash
sleep 5
mongosh --host shard3a:27020 <<EOF
    load('./scripts/shard3-setup.js')
EOF
```

Ele espera 5 segundos para que os outros containers acabem de inicializar e executar o comando. Primeiramente vai acessar o `mongosh` do primeiro container `shard3a` com `mongosh --host shard3a:27020` e irá executar `shard3-setup.js`.

```js
rs.initiate(
    {
       _id: "shard3",
       version: 1,
       members: [
          { _id: 0, host : "shard3a:27020", priority: 2},
          { _id: 1, host : "shard3b:27020", priority: 1},
          { _id: 2, host : "shard3c:27020", priority: 0}
       ]
    }
)
```

Neste script ele inicializa o replica set do shard3 definindo todos os membros e as prioridades para quem deve ser o primário, sendo quanto maior o número maior a chance de ser o primário. Assim que ele finaliza a tarefa o container para.

#### Router Setup

![Router Setup Arquitecture](./imagens/arqRouterSetup.png 'Router Setup Arquitecture')

O passo final é criar o router para cuidar das requisições da aplicação.

```yaml
mongo-router1:
    image: mongo
    container_name: router1
    networks:
      - mongoLojas
    ports:
      - 27017:27017
    depends_on:
      - config-srv-setup
      - shard1-setup
      - shard2-setup
      - shard3-setup
    command: ['mongos', '--port', '27017', '--configdb', 'config-server/config1:27017,config2:27017,config3:27017', '--bind_ip_all']
```

O passo final é criar o router para cuidar das requisições da aplicação. Criamos um container com a imagem `mongo` e colocamos eles na mesma rede `mongoLojas`. Sendo o último passo ele tem que esperar inicializar os containers anteriores, `config-srv-setup, shard1-setup, shard2-setup, shard3-setup`, para inicializar. Quando finalizar a inicialização o seguinte comando será executado para configurar o `mongos`, `mongos --port 27017 --configdb config-server/config1:27017,config2:27017,config3:27017 --bind_ip_all'`

- `--port 27017`: Define o port como 27017.
- `--configdb config-server/config1:27017,config2:27017,config3:27017`: Define qual é config server.
- `--bind_ip_all`: Vai juntar todos os ips em um só.

```yaml
router-setup:
    image: mongo
    container_name: router-setup
    volumes:
      - .\scripts:/scripts
    depends_on:
      - mongo-router1
    networks:
      - mongoLojas
    restart: no
    entrypoint: ['bash', './scripts/start-router.sh']
```

Agora falta adicionar os shards do cluster, para isso temos que fazer o setup do router. Precisamos colocar na mesma rede `mongoLojas` e mapear a pasta `script` para poder usar os scripts depois. Aguardamos o `mongo-router1` acabar a inicialização e executar o script `start-router.sh`.

```bash
sleep 30
mongosh --host router1:27017 <<EOF
    sh.addShard("shard1/shard1a:27018")
    sh.addShard("shard1/shard1b:27018")
    sh.addShard("shard1/shard1c:27018")
    sh.addShard("shard2/shard2a:27019")
    sh.addShard("shard2/shard2b:27019")
    sh.addShard("shard2/shard2c:27019")
    sh.addShard("shard3/shard3a:27020")
    sh.addShard("shard3/shard3b:27020")
    sh.addShard("shard3/shard3c:27020")
EOF
```

Aguardamos 30 segundos para os outros containers finalizarem a inicialização e acessamos o router usando `mongosh --host router1:27017`. Cada shard\subshard deve ser adicionado individualmente.

#### Pre-requisitos

- Docker
  - Docker compose
- Python
  - pip
- MongoDB Compass

#### Como Executar

Para executar segue os seguintes passos:

1. Abre o terminal clona o repositorio
   `git clone https://github.com/joaomsv/PosNoSQL.git`
2. Execute o docker compose
   `docker compose up -d`
3. Instale as dependencias
   `pip install -r requirements.txt`
4. Aguarde 30 segundos
5. Execute o script para criar e alimentar os bancos
    - Windows: `py .\seed.py`
    - Outros: `python3 ./seed.py`
6. Acesse o cluster usando o link
   `mongodb://localhost:27017/`

### Testes

#### Seeding Filiais

![Performance Teste Dos Insert de Filial](./imagens/filialInsert.png 'Performance Teste Dos Insert de Filial')

Injetando 100k de filial resultou nesses gráficos, foi feito um limitação de `chunksize` de 5 e usando um ranged shard key no `shard_key` definido antes do insert.

#### Seeding Produtos

![Performance Teste Dos Insert de Produto](./imagens/produtoInsert.png 'Performance Teste Dos Insert de Produto')

Injeção de 5 batches de 100k de produto resultou nesses gráficos, foi feito um limitação de `chunksize` de 5 e usando um hashed shard key no `shard_key` definido após o insert.

#### Teste Consulta de Produtos

![Teste Consulta de Produtos](./imagens/testFindProdutos.png 'Teste Consulta de Produtos')

#### Teste Update de Inventario

![Teste Update de Inventario](./imagens/testUpdateProduto.png 'Teste Update de Inventario')

#### Teste Add Novos Filiais

![Teste Add Novos Filiais](./imagens/testAddFilial.png 'Teste Add Novos Filiais')

### Recommendações Finais
