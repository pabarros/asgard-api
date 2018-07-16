#encoding: utf-8

from enum import Enum
import traceback
import sys
import logging

import pkg_resources
from simple_json_logger import JsonLogger

from hollowman.log import logger
from hollowman import conf

class API_PLUGIN_TYPES(Enum):
    API_METRIC_PLUGIN = "asgard_api_metrics_mountpoint"

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
# É isso que diz à UI para voltar e pegar o main.js

PLUGIN_REGISTRY = {
}

PLUGINS_LOAD_STATUS = {
    'plugins': {
    },
    "stats": {
        "load_ok": 0,
        "load_failed": 0,
        "load_total": 0,
    }
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
    return {'plugins': list(PLUGIN_REGISTRY.values())}

def get_pulgin_load_status_data():
    return PLUGINS_LOAD_STATUS

def load_entrypoint_group(groupname):
    return list(pkg_resources.iter_entry_points(group=groupname))

def get_plugin_logger_instance(plugin_id):
    json_logger = JsonLogger(flatten=True, extra={"plugin-id": plugin_id})
    return json_logger


def load_all_metrics_plugins(flask_application, get_plugin_logger_instance=get_plugin_logger_instance):
    all_metric_plugins = load_entrypoint_group(API_PLUGIN_TYPES.API_METRIC_PLUGIN.value)
    for entrypoint in all_metric_plugins:
        try:
            package_name = entrypoint.dist.project_name
            if package_name not in PLUGINS_LOAD_STATUS['plugins']:
                PLUGINS_LOAD_STATUS['plugins'][package_name] = []

            entrypoint_function = entrypoint.load()
            plugin_logger_instance = get_plugin_logger_instance(plugin_id=package_name)
            plugin_logger_instance.setLevel(getattr(logging, conf.LOGLEVEL, logging.INFO))
            plugin_data = entrypoint_function(logger=plugin_logger_instance)
            url_prefix = f"/_cat/metrics/{package_name}"
            flask_application.register_blueprint(plugin_data['blueprint'], url_prefix=url_prefix)
            logger.info({
                "msg": "Metrics plugin loaded",
                "plugin_entrypoint": entrypoint,
                "plugin_id": package_name,
                "mountpoint URI": url_prefix,
            })
            PLUGINS_LOAD_STATUS['plugins'][package_name].append({
                "status": "OK",
                "plugin_id": package_name,
                "entrypoint": {
                    "module_name": entrypoint.module_name,
                    "function_name": entrypoint.attrs[0],
                }
            })
            PLUGINS_LOAD_STATUS["stats"]["load_ok"] += 1
            PLUGINS_LOAD_STATUS["stats"]["load_total"] += 1
        except Exception as e:
            formatted_traceback = traceback.format_exc()
            exception_type = sys.exc_info()[0].__name__
            logger.error({
                "msg": "Failed to load plugin",
                "plugin_entrypoint": entrypoint,
                "plugin_id": package_name,
                "traceback": formatted_traceback,
                "type": exception_type,
            })
            PLUGINS_LOAD_STATUS['plugins'][package_name].append({
                "status": "FAIL",
                "exception": exception_type,
                "traceback": formatted_traceback,
                "plugin_id": package_name,
                "entrypoint": {
                    "module_name": entrypoint.module_name,
                    "function_name": entrypoint.attrs[0],
                }
            })
            PLUGINS_LOAD_STATUS["stats"]["load_failed"] += 1
