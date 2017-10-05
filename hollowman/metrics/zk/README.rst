

README
======


API bem simples para termos pelo menos algum numero sobre o cluster de Zookeeper.

O IPs dos servers são passados em envs nesse formato: `HOLLOWMAN_METRICS_ZK_ID_<N>=<IP>`

Onde:

* `<N>` é um número, e começa do `0`;
* `<IP>` é p IP do servidor com ID `<N+1>` no cluster de ZK


Endpoints
=========


/leader
-------

Reorna um json com uma chave, contendo o ID do zookeeper que é o atual ider:

```
{"leader": 2}
```

Retorna `{"leader": 0}` se não houver líder.


/zk/<n>
-------

Retorna métricas individuais sobre o ZK server com ID=<n>.

```
{
"outstanding" : 0,
"latency_avg" : 0,
"is_leader" : 0,
"mode" : "follower",
"connections" : 4,
"node_count" : 932,
"latency_max" : 1146,
"latency_min" : 0
}
```
