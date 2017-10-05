

from collections import defaultdict


def _dummy_parser(data):
    return {}

def _parse_latency_line(data):
    _min, _avg, _max = data.split("/")
    return {
        "latency_min": int(_min),
        "latency_avg": int(_avg),
        "latency_max": int(_max),
    }

def _parse_mode_line(data):
    value = data.strip()
    return {
        "mode": value,
        "is_leader": 1 if (value == "leader") else 0
    }

def _parse_connections(data):
    return {"connections": int(data)}

def _parse_oustanting(data):
    return {"outstanding": int(data)}

def _parse_node_count(data):
    return {"node_count": int(data)}

STAT_LINE_PARSER_CALLBACK = defaultdict(lambda: _dummy_parser)

_call_backs = {
    'latency min/avg/max': _parse_latency_line,
    'connections': _parse_connections,
    'outstanding': _parse_oustanting,
    'mode': _parse_mode_line,
    'node count': _parse_node_count,
}

STAT_LINE_PARSER_CALLBACK.update(_call_backs)

def parse_stat_output(raw_output):
    result_dict = {}
    lines = [l.lower() for l in raw_output.split("\n") if ":" in l]
    for line in lines:
        key, value = line.split(":", 1)
        parsed = STAT_LINE_PARSER_CALLBACK[key.strip()](value)
        result_dict.update(parsed)

    return result_dict

