import abc
from typing import List, Optional

from asgard.models.account import Account
from asgard.models.agent import Agent
from asgard.models.app import App
from asgard.models.task import Task
from asgard.models.user import User


class AppsBackend(abc.ABC):
    @abc.abstractmethod
    async def get_apps_definition(
        self, user: User, account: Account
    ) -> List[App]:
        """
        Retorna a definição de todas as Apps da conta Account
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, app_id: str, user: User, account: Account
    ) -> Optional[App]:
        """
        Retorna a definicão de uma app, com id `app_id`.
        Ess app deve existir na conta `account`
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_tasks(self, app: App) -> Optional[Task]:
        """
        Retorna todas as instâncias atualmente rodando para a App `app`.
        """
        raise NotImplementedError


class AgentsBackend(abc.ABC):
    @abc.abstractmethod
    async def get_agents(self, user: User, account: Account) -> List[Agent]:
        """
        Retorna todos os Agents da conta `account`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_by_id(
        self, agentd_id: str, user: User, account: Account
    ) -> Optional[Agent]:
        """
        Retorna o agent de id `agentd_id` pertencente à conta `account`
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_apps_running(self, user: User, agent: Agent) -> List[App]:
        """
        Retornas lista de App que está rodando nesse agent
        """
        raise NotImplementedError


class Orchestrator(metaclass=abc.ABCMeta):
    """
    Classe abstrata que mapeia todas as ações que um orquestrador pode excutar.
    As depdenências injetadas aqui são implementações que efetivamente falam com cada um dos backends suportados.
    """

    def __init__(
        self, agents_backend: AgentsBackend, apps_backend: AppsBackend
    ) -> None:
        self.agents_backend = agents_backend
        self.apps_backend = apps_backend

    @abc.abstractmethod
    async def get_agents(self, user: User, account: Account) -> List[Agent]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get_apps_running_for_agent(
        self, user: User, agent: Agent
    ) -> List[App]:
        """
        Método que retorna todas as apps que estão atualmente rodando no agent referido.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def get_agent_by_id(
        self, agent_id: str, user: User, account: Account
    ) -> Optional[Agent]:
        raise NotImplementedError
