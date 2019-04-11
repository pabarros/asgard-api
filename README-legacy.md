## Arquitetura geral da API (legado)

Esse documento existe apenas para ilustrar como é (era) a arquiterura da API legada, escrita em flask.

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
