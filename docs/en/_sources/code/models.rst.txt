.. _asgard.models:

Models
======


Os models são os objetos que todo o codebase da Asgard API deve usar para transitar informações entre suas camadas, desde o request HTTP que chegou no endpoint até o momento em que temos que falar com a API do :ref:`Orquestrador <asgard.backends.orquestrador>` real.



Existem alguns tipos de modelo no projeto:


- :ref:`Asgard Models <asgard.models.base>`, estão no pacote :py:mod:`asgard.models`
- :ref:`Backend Models <asgard.models.backend>`, estão no pacote ``asgard.backends.*.models``
- :ref:`Client Models <asgard.models.client>`, estão o pacote ``asgard.backends.*.client.models``

Abaixo temos uma explicação sobre cada um deles.


.. _asgard.models.base:

Asgard Models
-------------

Esses são models abstratos que servem de modelo Base para os modelos que estão em ``asgard.backends.*.models``. A ideia é ter um modelo único para todos os backends, dessa forma mesmo que tenhamos múltiplos backends retornando cada um seus modelos, todos serão filhos dos "BaseModels" que estão em ``asgard.models.*``.

Imagine que temos duas implementações de :ref:`AgentsBackend <asgard.backends>`:

- MesosAgentsBackends
- K8sAgentsBackend

nesse caso teríamos os respectivos models em:

- ``asgard.backends.mesos.models.agent.Agent``
- ``asgard.backends.k8s.models.agent.Agent``

Ambos os models seriam declarados dess forma:

.. code:: python

  from asgard.models.agent import Agent

  class MesosAgent(Agent):
    type: str = "MESOS"

  class K8SAgent(Agent):
    type: str = "K8S"

Ambos os models podem ter métodos/campos específicos do seus backends, mas ao mesmo tempo precisam preencher os campos exigidos pelo model base, :py:class:`asgard.models.agent.Agent`.

Isso significa que podemos ter em uma mesma lista (``agents: List[Agent]``) objetos de dos dois backends, pois eles são filhos da mesma classe base. Extrapolando isso para um momento onde temos que listar os agents desses dois backends, poderíamos fazer algo como:

.. code:: python

  import asyncio
  from typing import List

  from asgard.backends.base import AgentsBackend
  from asgard.backends.k8s.impl import K8SAgentsBackend
  from asgard.backends.mesos.impl import MesosAgentsBackend
  from asgard.models.account import Account
  from asgard.models.agent import Agent
  from asgard.models.user import User


  async def get_all_agents(
      user: User, account: Account, *agents_backends: AgentsBackend
  ) -> List[Agent]:
      m_agents = await agents_backends[0].get_agents(user, account)
      k_agents = await agents_backends[1].get_agents(user, account)
      return m_agents + k_agents


  async def main():
      mesos_agents_bakend = MesosAgentsBackend()
      k8s_agents_backend = K8SAgentsBackend()
      user = User(...)
      account = Account(...)
      return await get_all_agents(
          user, account, mesos_agents_bakend, k8s_agents_backend
      )

Essa é a ideia principal dos models: Ter objetos comuns que podem ser passados e combinados com objetos do mesmo tipo mas providos por outras implementações.


.. _asgard.models.backend:

Backend Models
--------------

Os Models de cada backend são, na vedade, implementações do modelos abstratos. Eles podem conter campos/métodos específicos de cada backend mas precisam implementar todos os métodos abstratos exigidos pelos ``asgard.models.*``.

Cada backend model deve definir o valor do seu campo ``type``. Esse campo é uma string e pode ser escolhido livremente pela implementação do backend. Esse campo é serializado junto com o modelo e serve para diferenciar de qual backend aquele objeto veio.


.. _asgard.models.client:

Client Models
-------------


Os Client Models são models usados internamente pelos backends. Cada implementação de :ref:`asgard.backends` precisa falar com uma API para implementar suas funcionalidades, por exemplo, o :py:class`asgard.backend.mesos.impl.MesosAgentsBackend` por exemplo precisa falar com a API do `mesos <https://mesos.apache.org>`_ para fornecer os dados corretos.

A ideia é que cada backend tenha seus próprios clients que também recebem (como parâmetro) e retornem **modelos**. Os Client Models depois são transformados em Backend Models para poderem ser serializados pela API HTTP do asgard.


O Client model é o mapeamento bruto do que a API do backend retorna. Então pegando um exemplo de retorno da API do Mesos, endpoint `/slaves <http://mesos.apache.org/documentation/latest/endpoints/master/slaves/>`_.


::

  {
    "slaves": [
      {
        "id": "4783cf15-4fb1-4c75-90fe-44eeec5258a7-S12",
        "hostname": "10.234.172.35",
        "port": 5051,
        "attributes": {
          "workload": "general",
          "owner": "asgard"
        },
        "active": true,
        "version": "1.4.1"
      }
  }


Um possível mapeamento de Client Model para essa resposta poderia ser:

.. code:: python


  from typing import Dict, Type

  from pydantic import BaseModel as PydanticBaseModel

  from asgard.backends.mesos.models.agent import MesosAgent as AsgardMesosAgent


  class MesosAgent(PydanticBaseModel):
      id: str
      hostname: str
      port: int
      attributes: Dict[str, str]
      version: str
      active: bool

.. note::
  Esse model estaria em ``asgard.backends.mesos.client.models.agent.MesosAgent``

A responsabilidade se transformar em Backend Model é do próprio Client Model. A forma que escolhemos de transformar um Client Model em seu respectivo Backend Model é adicionando um método chamado ``to_asgard_model()`` que recebe a classe do Backend Model para o qual será transformado.

Pegando ainda esse exemplo, essa seria um possível implementação da transformação de Client Model para Backend Model.


.. code:: python

    def to_asgard_model(
        self, class_: Type[AsgardMesosAgent]
    ) -> AsgardMesosAgent:
        return class_(
            id=self.id,
            hostname=self.hostname,
            port=self.port,
            labels=self.attributes,
            version=self.version,
            ativo=self.active,
        )

Esse é o código que deve "traduzir" os campos da API do backend para os campos do modelo que será usado por todo o código do Asgard.
