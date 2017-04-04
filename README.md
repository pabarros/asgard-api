# Hollowman

The thought of human invisibility has intrigued man for centuries. Highly gifted scientist Sebastian Caine develops a serum that induces complete invisibility. His remarkable transformation results in unimaginable power that seems to suffocate his sense of morality and leads to a furious and frightening conclusion.

![Hollowman](https://bytebucket.org/sievetech/hollowman/raw/f6fa51242599cf5c659371e725c440da61b02453/hollowman.jpg?token=4d80dc08d24e9ddb42ef8ef0eea371d5d699f3f8)

## Env vars
* MARATHON_CREDENTIALS [required] user:pass for the basic auth
* MARATHON_ENDPOINT [required] Where to connect to find marathon api

* HOLLOWMAN_FILTER_DNS_ENABLE: "1|0" Diz se o filtro de DNS estará ligado ou desligado
* HOLLOWMAN_REDIRECT_ROOTPATH_TO: Env que diz para onde o usuario será redirecionado se acessar a raiz onde o hollowman está deployado. Defaults to `/v2/apps`


## Opções específicas de filtros

# DNS
 * hollowman.filter.dns.disable: Label que define se o filtro de dns está ligado para uma app específica.

# FORCE PULL
 * hollowman.filter.forcepull.disable: Label que define se o checkbox de forcepull não será marcado automaticamente para uma app específica


## Running tests
`py.test --cov=hollowman --cov-report term-missing -v -s`
