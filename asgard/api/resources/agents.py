from typing import List

from asgard.services.models.agent import Agent
from asgard.services.models import Model


class AgentsResource(Model):
    """
    O campo `agents` deveria ser anotado com `List[Agent]`, mas o problema é que o pydantic, no momento em que vai criar esse campo,
    instancia um objeto Agent. Mas esse objeto é apenas um objeto Base para os vários typos de agents que teremos (MesosAgent, KubernetesAgent, etc).

    O problema é que, como ele instancia `Agent(**data)` e o objeto Agent não tem nenhum campo declarado, no final temos um objeto vazio;

    ipdb> AgentsResource(agents=[agents[0].dict()])
    <AgentsResource agents=[<Agent type='MESOS'>]>
    ipdb> MesosAgent(**agents[0].dict())
    <MesosAgent type='MESOS' id='ead07ffb-5a61-42c9-9386-21b680597e6c-S44' hostname='172.18.0.18' active=True version='1.4.1' port=5051 used_resources={'disk': '0', 'mem': '512', 'gpus': '0', 'cpus': '0.5', 'ports': '[31858-31858]… attributes={'mesos': 'slave', 'workload': 'general', 'dc': 'aws', 'owner': 'dev'} resources={'disk': '26877', 'mem': '2560', 'gpus': '0', 'cpus': '2.5', 'ports': '[30000-3…>
    ipdb> AgentsResource(agents=agents)
    <AgentsResource agents=[<Agent type='MESOS'>]>

    O ideal é que pudéssemos ter:
    ipdb> AgentsResource(agents=agents)
    <AgentsResource agents=[<MesosAgent type='MESOS' id='ead07ffb-5a61-42c9-9386-21b680597e6c-S44' hostnam…>
    ipdb>

    Mas esse jeito só funciona se o campo *não estiver anotado*, mas aí podemos passar qualquer coisa, não só `List[Agent]`.

    A ideia de user List[Union[MesosAgent, ...]] é ruim pois a cada novo tipo de Agent teríamos que voltar nesse código e alterar.
    Se pensarmos em uma interface plugável, isso se torna inviável.

    """

    agents = []  # type: List[Agent]
