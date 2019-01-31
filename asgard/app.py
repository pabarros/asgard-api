from asyncworker import App
from asgard import conf

app = App(
    host=conf.ASGARD_RABBITMQ_HOST,
    user=conf.ASGARD_RABBITMQ_USER,
    password=conf.ASGARD_RABBITMQ_PASS,
    prefetch_count=conf.ASGARD_RABBITMQ_PREFETCH,
)
