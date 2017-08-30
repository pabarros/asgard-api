#encoding: utf-8

import logging
from simple_json_logger import JsonLogger

logger = JsonLogger(flatten=True)
logger.setLevel(logging.INFO)
