
## Como contriuir como o projeto

Esse documento descreve como rodar uma versão local do Projeto Asgard.

## Rodando componentes da infra-estrutura

Para rodar a infra-estrutura, atualmente Mesos + Marathon, você precisa
ter o docker instalado. O ideal é ter uma versão aualizada, pelo menos `17.x`.

Rode em um terminal separado, o script `asgard-run.sh`. Esse script vai subir um cluster
Mesos + Marathon + PGSQL. O Script imprime os IPs de cada um dos componenetes para que
possamos saber onde estão rodando.

O PGSQL já está com a estrutura do banco pronta e já possui um usuário com o Token `<TOKEN-AQUI>`.

Dessa forma você jaá consegue fazer o seguinte request:

`curl -i -H "Authorization: Token <TOKEN-AQUI>" http://127.0.0.1:5000/v2/apps`

E isso deve retornar:

```
{"apps": []}
```

## Instalando as dependencias do asgard-api

Instale as dependencias listadas em `requirements-dev.txt`.

## Rodando o projeto

Para rodar o projeto você precisa passar algumas envvars. Elas estão listadas no `README.md`.

Importante passar as envs 

`HOLLOWMAN_REDIRECT_AFTER_LOGIN=http://localhost/authenticated`
`HOLLOWMAN_CORS_WHITELIST=http://localhost`

## Rodando a UI

Para rodar aa UI você precisa fazer o clone do repositorio `https://github.com/b2w-bit/asgard-ui`.
Você precisa também ter o Nodejs `5.4.1`, isso é uma dependencia do Marathon UI e portando devemos
obedecer (por enquanto).

Faça o build da imagem (com `-t asgard-ui`) da UI e rode com esse comando (estando na raiz do projeto asgard-ui)

`docker run --rm --net=host -e SIEVE_LOGIN_REDIRECT=http://127.0.0.1:5000/login/google -v ${PWD}:/opt/app asgard-ui`

...to be continued...

