from asgard.models import Task


class MesosTask(Task):
    _type: str = "MESOS"
    typer: str = "MESOS"

    name: str

    def transform_to_asgard_task_id(executor_id: str) -> str:
        task_name_part = executor_id.split("_")[1:]
        return "_".join(task_name_part)
