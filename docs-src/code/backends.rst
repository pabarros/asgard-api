.. _asgard.backends:

Backends
========


Os Backends são a implementaçao concreta com as outras APIs com as quais a Asgard API consegue se comunicar.

Na mesma linha dos :ref:`Services <asgard.services>`, esses objetos devem mapear todas as ações que um determinado backend deve ser capaz de realizar.

O backend são dividiso em ``AgentsBackend`` e ``AppsBackends``. Esss são objetos abstratos que definem quais ações cada um desses backends podem executar.

A junção de múltiplos ``Backends`` forma um "Orquestrador", modelado no objeto ``Orchestrator``. Esse é o objeto principal em termos de funcionalidades da Asgard API, é esse objeto quem define o que a Asgard API consegue fazer, em termos de orquestração.

Abaixo está a implementação do objeto ``Orchestrator``

.. literalinclude:: ../../asgard/backends/base.py

A asgard API suporte alguns Backends:

- Mesos
- Marathon
