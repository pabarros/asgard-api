from asgard.backends.marathon.impl import MarathonAppsBackend
from asgard.backends.mesos.impl import MesosOrchestrator, MesosAgentsBackend

mesos = MesosOrchestrator(MesosAgentsBackend(), MarathonAppsBackend())
