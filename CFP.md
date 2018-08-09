# CFP oficial

Texto oficial para submissão de palestras em eventos.


# Texto oficial

ASGARD: Abstraindo orquestradores de containers 

# Pontos principais

1. Apresentar a arquitetura do ASGARD, a plataforma desenvolvida para abstrair o orquestrador Marathon;
2. Como o ASGARD ajudou nossos times de desenvolvimento a sair de um esforço de horas para minutos no deploy;
3. Como o desenvolvimento do projeto ASGARD contribui para a evolução do Projeto open-source Marathon UI.

# Resumo:

O ASGARD é uma plataforma open-source que foi desenvolvida para abstrair, inicialmente, o orquestrador Marathon. Ela tem como benefícios simplificar o deploy das aplicações, pelos times de dev, uma vez que eles podem abstrair a existência do orquestrador, focando 100% na aplicação que está sendo desenvolvida; 

Essa plataforma adiciona funcionalidades como autenticação, isolamento para múltiplos times (multi tenant) e permissionamento (implementação futura).

Nesta palestra será apresentado o motivacional que levou ao desenvolvimento do ASGARD; o antes-e-depois das equipes que hoje utilizam o ASGARD; a arquitetura do ASGARD e como ela pode se tornar um multiorquestrador no futuro.


# Informações adicionais:

O ASGARD, como projeto, começou a ser desenvolvido por um time que era especializado em infra/backend e por esse motivo acabou-se priorizando não fazer uma interface web do zero (muito trabalho e sem dev front-end). Escolheu-se, então, utilizar como interface do ASGARD o Marathon UI, open-source, e injetar a ASGARD API entre a Marathon API e a ASGARD UI.  

Foi preciso fazer com que o ASGARD API tivesse comportamento idêntico ao da Marathon API mas com comportamentos adicionais, sem mexer no código do Marathon API. 

Na evolução do ASGARD, como projeto, foi preciso fazer alterações no Marathon UI para que fosse possível escrever plugins que fizesse o que o projeto ASGARD precisa (ex. Autenticação, botões e janelas para fazer troca de conta, etc). Essas alterações realizadas foram submetidas para o projeto original (Marathon UI) e já foram aceitas[1][2]. A intenção é manter esse ciclo para fortalecer o projeto original (Marathon UI) para que o projeto dê oportunidade de terceiros escreverem plugins mais ricos e absorver para o ASGARD modificações que terceiros eventualmente farão no Marathon UI.

[1] https://github.com/mesosphere/marathon-ui/pull/813
[2] https://github.com/mesosphere/marathon-ui/pull/819
