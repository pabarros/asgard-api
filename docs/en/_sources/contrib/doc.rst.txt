
Contribuindo com o projeto
==========================

Atualizando a documentação do projeto
--------------------------------------------------


A documentação do projeto é feita com sphinx. A língua padrão para a documentação é `pt_BR`, mas traduções podem ser feitas para outras línguas. As configurações já estão preparadas para traduzir para `en`.

A tradução é feita segundo a recomendação do projeto sphinx, que é usando gettext.

Gerando a versão html da documentação
--------------------------------------------------

Para gerar a versão final da documentação, entre na pasta `docs-src` e rode:

pipenv run make docs

Isso vai gerar todas as documentações, em todas as línguas configuradas. Atualmente `pt_BR` em `en`. A documentação `pt_BR` será gerada na pasta `docs/` e as traduçõees estarão também dentro dessa pasta, abaixo de sub-pastas com o código da língua escolhida.

por exemplo, a tradução para `en` estará em `docs/en`.


.. toctree::
   :maxdepth: 2

   writing-tests.rst
