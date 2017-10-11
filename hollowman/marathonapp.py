

from marathon.models.app import MarathonApp


class SieveMarathonApp(MarathonApp):

    def get_constraint_by_name(self, consraint_name):
        result = []
        for c in self.constraints:
            if c.field == consraint_name:
                result.append(c)
        return result

    def remove_constraint_by_name(self, consraint_name):
        result = []
        for c in self.constraints:
            if c.field != consraint_name:
                result.append(c)
        self.constraints = result

