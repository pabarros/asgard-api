from asgard.models.app import App


class MesosApp(App):
    type: str = "MESOS"

    def transform_to_asgard_app_id(executor_id: str) -> str:
        task_name_part = executor_id.split(".")[0]
        return "/".join(task_name_part.split("_")[1:])
