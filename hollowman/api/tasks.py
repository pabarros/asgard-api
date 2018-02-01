
import json
import requests

from flask import Blueprint, Response
from hollowman.decorators import auth_required
from hollowman.conf import MESOS_ADDRESSES

tasks_blueprint = Blueprint(__name__, __name__)


def get_task_data(task_id):

    task_id_with_namespace = task_id
    task_info = requests.get(f"{MESOS_ADDRESSES[0]}/tasks?task_id={task_id_with_namespace}").json()['tasks'][0]

    framework_id = task_info['framework_id']
    slave_id = task_info['slave_id']

    slave_info = requests.get(f"{MESOS_ADDRESSES[0]}/slaves?slave_id={slave_id}").json()['slaves'][0]
    slave_ip = slave_info['hostname']

    slave_state = requests.get(f"http://{slave_ip}:5051/state").json()
    framework_info = [fwk for fwk in slave_state['frameworks'] if fwk['id'] == framework_id][0]
    execuor_info = [executor for executor in framework_info['executors'] if executor['id'] == task_id_with_namespace]
    if not execuor_info:
        execuor_info = [executor for executor in framework_info['completed_executors'] if executor['id'] == task_id_with_namespace]

    if execuor_info:
        execuor_info = execuor_info[0]
    sandbox_directory = execuor_info['directory']
    return (slave_ip, sandbox_directory)


@tasks_blueprint.route("/<string:task_id>/files")
@auth_required(pass_user=True)
def task_files_list(task_id, user):
    namespace = user.current_account.namespace
    slave_ip, sandbox_directory = get_task_data(f"{namespace}_{task_id}")
    files_info = requests.get(f"http://{slave_ip}:5051/files/browse?path={sandbox_directory}").json()

    return Response(response=json.dumps(files_info), status=200, mimetype="application/json")

@tasks_blueprint.route("/<string:task_id>/files/read/<path:filepath>")
#@auth_required()
def task_files_read(task_id, filepath):
    pass

@tasks_blueprint.route("/<string:task_id>/files/download/<path:filepath>")
#@auth_required()
def task_files_download(task_id, filepath):
    """
        Fazer stream do resposne do mesos para o nosso response.
        Dessa forma não precisams ler todo o arquivo antes de começar a enviar para o client
    """
    pass
