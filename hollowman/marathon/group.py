import re
import marathon.models.base

marathon.models.base.ID_PATTERN = re.compile(".*")
from marathon.models.group import MarathonGroup


class AsgardAppGroup:
    def __init__(self, wrapped_group=MarathonGroup()):
        self._marathon_group = wrapped_group

    @property
    def id(self):
        return self._marathon_group.id

    def __eq__(self, other):
        return self.id == other.id

    def from_json(self, data):
        self._marathon_group = MarathonGroup.from_json(data)
        return self

    def __iterate(self, groups):
        for g in groups:
            yield g
            if g.groups:
                yield from self.__iterate(g.groups)

    def iterate_groups(self):
        yield self._marathon_group
        yield from self.__iterate(self._marathon_group.groups)

    def iterate_apps(self):
        for g in self.iterate_groups():
            for app in g.apps:
                yield app

    @classmethod
    def from_json(cls, *args, **kwargs):
        return AsgardAppGroup(MarathonGroup.from_json(*args, **kwargs))
