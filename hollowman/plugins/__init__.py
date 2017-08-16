#encoding: utf-8

# Registry é um dict onde a key é o ID do plugin e o value
# são meta-dados sobre o plugin, ex:
#    * ID do plugin
#    * Quais permissões são necessárias para que esse plugin possa ser carregado

# Cada plugins é composto por apenas um arquivo js (main.js), gerado pelo webpack e colocado
# aqui nesse repositório, em `/static/plugins/<plugin-id>/main.js`.

# Todo plugin dever ter o trecho:
#         "info" : {
#            "modules" : [
#               "ui"
#            ],
#         },
# É isso que diz à UI para voltar e paagr o main.js

PLUGIN_REGISTRY = {
}

def register_plugin(plugin_id):
    plugin_data = {
        "id": plugin_id,
        "info": {
            "modules": ["ui"]
        }
    }
    PLUGIN_REGISTRY[plugin_id] = plugin_data

def get_plugin_registry_data():
    data = {
        "plugins": []
    }
    for key, value in PLUGIN_REGISTRY.items():
        data["plugins"].append(value)

    return data
