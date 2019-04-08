.. _asgard.services:

Services
========


Service faz o papel da "ponte" entre os endpoints HTTP e todo restante do código. E ideia é que os endppints HTTP só consigam interagir com o restante do código através de um "Service".

A ideia dos "Services" é mapear todas as possíveis ações que a Asgard API pode executar.



Vejamos um exemplo:

O endpoint ``/agents`` é quem retorna a lista de agents de um cluster. Esse endpoints HTTP connhece apenas o ``AgentsService``. Ali estão todas as ações que os endpoints HTTP relacionados com ``Agents`` podem executar.

Aqui está a implementação do ``AgentsService``:

.. literalinclude:: ../../asgard/services/agents.py

Perceba como os métodos do ``AgentsService`` recebem objetos concretos em vez de tipos primitivos, esses são os :ref:`Models <asgard.models>`. A única exceção é quando precisamos buscar um objeto usando seu identificador único (``id``), nesse caso passamos o valor do ``id`` mesmo, já que essa busca é justamente quem vai fazer a troca de um "id" por um objeto preenchido.
