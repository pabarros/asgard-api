

from marathon.models.app import MarathonApp


class AsgardMarathonApp(MarathonApp):

    def get_constraints_by_name(self, consraint_name):
        result = []
        for c in self.constraints:
            if c.field == consraint_name:
                result.append(c)
        return result

    def remove_constraints_by_name(self, consraint_name):
        result = []
        for c in self.constraints:
            if c.field != consraint_name:
                result.append(c)
        self.constraints = result

    def has_constraint(self, name):
        return len(self.get_constraints_by_name(name))

    def update_label(self, label_name, label_value):
        """Updates a specific App label

        :label_name: TODO
        :label_value: TODO
        :returns: TODO

        """
        self.labels[label_name] = label_value
