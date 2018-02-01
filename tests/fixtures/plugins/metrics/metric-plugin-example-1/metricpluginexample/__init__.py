
from flask import Blueprint

my_metrics_blue_print = Blueprint(__name__, __name__)

def plugin_init_ok():
  return {
    'blueprint': my_metrics_blue_print
  }

def plugin_init_wrong_return():
    return {
        'blueprint': int(42)
    }

def plugin_init_exception():
    return 1/0

@my_metrics_blue_print.route("/ping")
def some_endpoint():
    return "Metrics Plugin Example 1 OK"




