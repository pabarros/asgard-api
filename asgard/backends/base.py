import abc


class Backend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def get_agents(self, namespace: str):
        raise NotImplementedError
