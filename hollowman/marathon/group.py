
import re
import marathon.models.base
marathon.models.base.ID_PATTERN = re.compile('.*')
from marathon.models.group import MarathonGroup


class SieveAppGroup(MarathonGroup):

    def __iterate(self, groups):
        for g in groups:
            yield g
            if g.groups:
                yield from self.__iterate(g.groups)

    def iterate_groups(self):
        yield self
        yield from self.__iterate(self.groups)

    def iterate_apps(self):
        for g in self.iterate_groups():
            for app in g.apps:
                yield app
