# Asgard API [![Build Status](https://travis-ci.org/B2W-BIT/asgard-api.svg?branch=master)](https://travis-ci.org/B2W-BIT/asgard-api) [![codecov](https://codecov.io/gh/B2W-BIT/asgard-api/branch/master/graph/badge.svg)](https://codecov.io/gh/B2W-BIT/asgard-api)

API principal do Projeto Asgard.

## Projeto Asgard

O Projeto Asgard existe com dois propósitos principais:

 - Facilitar a vida de quem desenvolve aplicações (de todo tipo);
 - Facilitar a vida de quem mantém uma infra-estrutura onde rodam centenas/milhares de aplicações

O primeiro ponto é alcançado provendo uma Interface WEB (em uma API) universal onde a pessoa 
responsável por um conjunto de aplicações possa ver, em um único lugar, todas as informações 
sobre essas aplicações, como por exemplo: Quantiade de CPU/RAM alocada, Logs recentes gerados por
cada instâncias dessas aplicações, lista das instâncias de cada aplicação, etc.

O segundo ponto é alcançado tendo um úniclo cluster onde rodam tasks de múltiplos times. Tendo uma
API que provê números referentes a esses times, como por exemplo: Total de tarefas, Total de servidores
conectados no cluster, ocupação (em termos de CPU/RAM) do pool de máquinas de cada time (e também ocupação
global, sem considerar times separados), etc.

## Features principais

 * Separação de múltiplos times usando a mesma interface mas vendo apenas suas próprias aplicações;
 * API plugável para geração de números e métricas sobre o cluster;
 * Visualização de Logs de cada tarefa dentro da própria interface.

## Ideia geral de implementação

A ideia da Asgard API é ser o único ponto com o qual qualquer código (ou pessoa) deve falar. Essa API
é quem vai abstrair todos os orquestradores suportados pelo projeto. A ideia do projeto é definir seus
próprios Endpoints e Resources genéricos o suficiente para poderem ser transformados/traduzidos em 
Endpoints e Resources específicos do orquestrador escolhido.

É a asgard API quem fala com os múltiplos orquestradores, é papel dela receber uma requisição da UI (ou
de um client HTTP qualquer), decidir para qual backend aquele request deve ser encaminhado e então ela
faz todas as transformações necessárias para mudar o request sendo recebido para um formato em que o
orquestrador em questão consiga entender.


## Componentes principais do Projeto Asgard

### Componentes essenciais

- Asgard API (esse repositório)
- Asgard UI, que é a UI oficial do projeto Asgard. (https://github.com/B2W-BIT/asgard-ui)
  - Essa é a UI original do Marathon, com algumas poucas modificações. Modificações não triviais foram submetidas com PRs ao projeto orginal e já foram mergeadas.
- https://github.com/B2W-BIT/asgard-ui-session-checker-plugin
  - Plugin para a UI do Asgard que adiciona o token JWT em todas as requisições feitas à API.

### Componentes opcionais

- https://github.com/B2W-BIT/asgard-api-plugin-metrics-mesos
  - Fornece métrica sobre o cluster de Mesos, caso seja esse o seu orquestrador escolhido;
- https://github.com/B2W-BIT/asgard-api-plugin-metrics-fluentd
  - Fornece métricas sobre os buffers do Fluentd, caso seja essa a solução escolhida para fazer a coleta dos logs das aplicações;
- https://github.com/B2W-BIT/asgard-log-ingestor
  - Ingestor genérico de logs que lê as linhas de log de um RabbitMQ e indexa em vários destinos possíveis (elasticsearch, cloudwatch logs, etc)
- https://github.com/B2W-BIT/asgard-counts-ingestor
  - Ingestor de metadados de logs, contendo apenas as contagens (de linhas de logs e de byes de logs) de cada aplicação. Esses dados são também lidos de um RabbitMQ e indexados em um elasticsearch.
- https://github.com/B2W-BIT/asgard-app-stats-collector
  - Coletor genérico de estatísticas de uso de CPU/RAM de todas as tarefas do cluster, indexa no elasticsearch já adicionando o nome da App original. Esse coletor será o responsável por falar com outros orquestradores, à medida que suporte a eles for sendo adicionado ao projeto.

## Orquestradores atualmente suportados

Atualmente a Asgard API suporta:

* Mesosphere Marathon (https://mesosphere.github.io/marathon/)
  - Confirmamos que funciona até a versão 1.4.12. Ainda não testamos com versões posteriores (`1.5.x`, `.1.6.x`) mas pretendemos fazer isso em algum momento.

## Arquitetura geral da API

A Asgard API, internamente, possui 4 "pipelines" principais:

  - Request WRITE pipeline;
  - Request READ pipeline;
  - Response WRITE pipeline;
  - Response READ pipeline.

Cada pipeline é composta por uma lista de "Filtros", um filtro pode fazer parte de mais de uma pipeline (até de todas se quiser). 
Um exemplo de filtro que está registrado em múltiplas pipelines é o [`namespace` filter](hollowman/filters/namespace.py).

Cada pieline possui um "contrato" que o filtro deve obedecer para que possa fazer parte dessa pipeline, que é o que veremos a seguir.

### Request READ pipeline

Essa pipeline roda sempre que a Asgard API recebe um request de leitura, ou seja, `GET`.

Essa pipeline não tem uma interface definida, já que o que faz mais sentido é implementar um filtro na pipeline `Response.READ`.


### Request WRITE pipeline

Essa pipeline roda sempre que a Asgard API recebe um request de escrita, ou seja, `POST, PUT, PATCH, DELETE`.

Interface de um filtro de escrita:

```python
class Filter:
  
    def write_task(self, user, request_task, original_task):
        """
        Método chamado para cada task (instância de App) que está sendo
        modificada pelo request atual.
        Esse método é chamad individualmente para cada task.

        request_task: Representação da task que está no request atual
        original_task: Representação da task que está atualmente em vigor.
        """
        ...
        return request_task

    def write(self, user, request_app, original_app):
        """
        Método chamado para cada App sendo modificada no request atual.

        request_app: Representação da App que está no request atual;
        original_app: Representação da app que está atualmente em vigor
        """
        ...
        return request_app
```

O filtro deve sempre retornar o objeto que está no request (modificado ou não). É essa representação
que será enviada ao orquestrador.

### Response READ pipeline

Essa pipeline roda sempre que a Asgard API recebe um request de escrita, ou seja, `GET`. Essa pipeline roda imediatamente
antes de devolvermos o response para o cliente original.

Interface do filtro:

```python
class Filter:

    def response(self, user, response_app, original_app) -> AsgardApp:
      return response_app
      
    def response_group(self, user, response_group, original_group):
      return response_group

    def response_deployment(self, user, deployment: MarathonDeployment, original_deployment) -> MarathonDeployment:
      return deployment
    
    def response_task(self, user, response_task, original_task):
      return response_task

    def response_queue(self, user, response_queue, original_queue):
      return response_queue

```

Cada método é chamado para cada um dos tipos de Resources que existem. Assim como nos filtros de escrita, os métodos
são chamados individualmente para cada Resource envolvido nessa response, ex: Se estamos respondedo com uma lista de Apps,
cada app será passada individualmente para o filtro, no método `response()`. 

Se o método retornar o próprio objeto ele será incluído no response final. Se for retornado `None`, esse Resource será **removido** do
response final. Dessa forma um filtro consegue ocultar certos dados antes do response ser enviado ao cliente final.

### Response WRITE pipeline

Essa pipeline ainda não é usada (e talvez até seja rmeovida no furuto). Para mexer no response, implemente um filtro na pipeline `Response.READ`.

### Filtros

Um filtro é a forma que encontramos de modificar tanto o request quanto o response que a Asgard API recebe.

Para adicionar um novo filtro a uma pipeline, mexemos no dicionário `FILTERS_PIPELINE`, que está em [dispatcher.py](hollowman/dispatcher.py)

### Filtros - Trabalho futuro

Atualimente os filtros ficam sempre dentro do código do projeto principal e são adicionados/removidos manualmente. Existe uma ideia
de criar uma interface de plugins para que filtros externos (instalados com `pip install ...`) possam ser adicionados ao código de forma
mais dinâmica.

# Contribuindo com o Projeto Asgard

Para rodar um ambiente de desenvolvimento local, podemos usar o script [asgard-run.sh](asgard-run.sh) que está na raiz do projeto. Esse script vai
subir um cluster de Mesos + Marathon automaticamente. O output do script te diz quais os IPs de cada um dos componentes.

Depois de ter o cluster rodando é hora de configurar as env vars para o seu projeto local. A lista de envs necessárias está no final desse documento.

Essa é lista de env já com os valores para o ambiente de desenvolvimento:

```
ASGARD_FILTER_TRANSFORMJSON_ENABLED=1
ASGARD_LOGLEVEL=DEBUG
HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID=""
HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET=""
HOLLOWMAN_SECRET_KEY=secret__

HOLLOWMAN_CORS_WHITELIST=http://localhost:4200,http://localhost
UWSGI_EXTRA_ARGS=--static-map2 /static=/opt/app --honour-stdin
HOLLOWMAN_REDIRECT_AFTER_LOGIN=http://localhost:4200/authenticated/
MARATHON_CREDENTIALS=marathon:secret

ASGARD_CACHE_KEY_PREFIX=asgard-api-dev/

HOLLOWMAN_MARATHON_ADDRESS_0=http://172.18.0.31:8080
HOLLOWMAN_METRICS_ZK_ID_0=172.18.0.2
HOLLOWMAN_METRICS_ZK_ID_1=172.18.0.3
HOLLOWMAN_METRICS_ZK_ID_2=172.18.0.4

HOLLOWMAN_DB_URL=postgresql://postgres:@172.18.0.41/asgard

HOLLOWMAN_MARATHON_ADDRESS_0=http://172.18.0.31:8080
HOLLOWMAN_MARATHON_ADDRESS_1=http://172.18.0.31:8080
HOLLOWMAN_MARATHON_ADDRESS_2=http://172.18.0.31:8080

HOLLOWMAN_MESOS_ADDRESS_0=http://172.18.0.11:5050
HOLLOWMAN_MESOS_ADDRESS_1=http://172.18.0.12:5050
HOLLOWMAN_MESOS_ADDRESS_2=http://172.18.0.13:5050

```
Você precisa passar todas as envs para ser posspivel rodar o código da API. O jeito mais simples de fazer isso é criar um arquivo chamado `.env`
na raiz do projeto. Esse arquivo já está no `.gitignore`, por isso não será comitado.

## Rodando a Asgard API localmente

O projeto Asgard API usa o `pipenv` e precisa do python 3.6. Antes de instalar as dependências, certifique que o python 3.6 esteja instalado em funcionando.
Para instalar as dependências rode:

```
pipenv install --dev
```

Para rodar, use:

```
pipenv run python hollowman/main.py
```

Quando tiver a API rodando, você pode fazer um request para validar:

```
$ curl -i http://127.0.0.1:5000/v2/apps/
{"msg": "Authorization token is invalid"}% 
```

Isso significa que você não está autenticado, o que é verdade, já que nem criamos seu novo usuário. Faremos isso agora.

## Criando um novo usuário para desenvolvimento

Para criar um novo usuário, você pode editar o arquivo [user.sql](scripts/sql/user.sql) a adicionar ali um trecho de SQL que vincula seu user a uma das contas
de dev que existem no banco. Usando um exemplo: Novo usuário tem email "mail@server.com", faríamos o seguinte:

```

INSERT INTO "user" (tx_name, tx_email, tx_authkey, bl_system) VALUES ('Novo User', 'mail@server.com', 'a648638d589740879f25bf55648ccc21', false);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/DEV'),
  (SELECT id from "user" where tx_email='mail@server.com')
);

INSERT INTO user_has_account (account_id, user_id) VALUES (
  (SELECT id from account where name = 'Asgard/INFRA'),
  (SELECT id from "user" where tx_email='mail@server.com')
);
```

Agora rode novamente o script que sobe o ambiente de desenvolvimento. Isso vai recriar todos os componentes, incluindo o baco de dados.

Dessa forma, agora podemos fazer a seguinte requisição:

```
curl -H "Authorization: Token a648638d589740879f25bf55648ccc21" http://127.0.0.1:5000/v2/apps
{"apps": []}% 
```

Agora sim você está vendo sua lista de apps, que obviamente é vazia. Nesse momento você está pronto
para começar a desenvolver novos códigos para a Asgard API.


## Evoluindo o banco de dados

Sempre que fizermos uma mudança no banco, vamos guardar o SQL na pasta `sql/` . Os arquivos têm nome prefixado por um número (`date +"%s"`),
pois isso indica a ordem em que deve ser rodados. Por enquanto vamos assim até migrar para um projeto que gerencie essas migrações.

Para pegar o SQL que o Alchemy gera para um model:
Abra o ipython (também passando as mesmas envs que você passou para rodar a API)

```python
>>> from sqlalchemy.schema import CreateTable
>>> from hollowman.models import <Model>
>>> from hollowman.models import engine
>>> print (CreateTable(Account.__table__).compile(engine))
```


## Env vars necessárias para o projeto
* ASGARD_CACHE_URL [required]: Enredeço do cache (Redis). No formato: `redis://<host>:<port>/<db>`
* MARATHON_CREDENTIALS [required] user:pass for the basic auth
* HOLLOWMAN_MARATHON_ADDRESS_INDEX [required] Where to connect to find Marathon api. List of Marathon IPs. <INDEX> starts at 0.
* HOLLOWMAN_MESOS_ADDRESS_INDEX [required] Where to connect to find Mesos API. List of Mesos IPs. <INDEX> starts at 0.
* ASGARD_CACHE_KEY_PREFIX: default `asgard-api/` Prefixo que será usado em todas as operações com o cache
* ASGARD_CACHE_DEFAULT_TIMEOUT default 60s; Tempo de expiração padrão das chaves de cache
* HOLLOWMAN_REDIRECT_ROOTPATH_TO: Env que diz para onde o usuario será redirecionado se acessar a raiz onde o hollowman está deployado. Defaults to `/v2/apps`
* HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_ID: ID da app Oauth2, registrado no console do Google
* HOLLOWMAN_GOOGLE_OAUTH2_CLIENT_SECRET: Secret dessa app.
* HOLLOWMAN_SECRET_KEY: Secret usado pelo Flask
* HOLLOWMAN_REDIRECT_AFTER_LOGIN: URL pra onde o usuário será redirecionado após o fluxo do oauth2. O redirect é feito pra: `URL?jwt=<token_jwt>`
* HOLLOWMAN_DB_ECHO: Define se os logs do SQLAlchemy estão ligados: Valores possíveis: 1|0. Default 0
* HOLLOWMAN_DB_URL: URL completa (com user, pwd, host, schema) do banco de dados: Formato: `postgresql://<user>:<pwd>@<host>/<schema>`
* ASGARD_LOGLEVEL: String indicando o loglevel a ser usado. Pode ser INFO, ERROR, DEBUG, WARNING, etc.


# Rodando os testes do projeto
`PIPENV_DONT_LOAD_ENV=1 pipenv run py.test --cov=./ --cov-report term-missing -v -s`
