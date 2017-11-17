from typing import Iterable
from flask import Response as FlaskResponse, request
import json

from hollowman.filters.basicconstraint import BasicConstraintFilter
from marathon.models import MarathonDeployment, MarathonQueueItem

from hollowman.marathonapp import SieveMarathonApp

from hollowman.filters.uri import AddURIFilter
from hollowman.filters.trim import TrimRequestFilter
from hollowman.filters.forcepull import ForcePullFilter
from hollowman.filters.appname import AddAppNameFilter
from hollowman.filters.namespace import NameSpaceFilter
from hollowman.hollowman_flask import OperationType, FilterType
from hollowman.filters.owner import AddOwnerConstraintFilter
from hollowman.filters.defaultscale import DefaultScaleFilter
from hollowman.http_wrappers.response import Response


FILTERS_PIPELINE = {
    FilterType.REQUEST: {
        OperationType.READ: (
        ),

        OperationType.WRITE: (
            AddURIFilter(),
            DefaultScaleFilter(),
            NameSpaceFilter(),
            ForcePullFilter(),
            TrimRequestFilter(),
            AddAppNameFilter(),
            BasicConstraintFilter(),
            AddOwnerConstraintFilter(),
        )
    },
    FilterType.RESPONSE: (
        AddAppNameFilter(),
        NameSpaceFilter(),
    )
}

# Keys que são multi-valor e que devem
# ser mergeados de forma especial quando
# juntamos a request_app com a original_app
REMOVABLE_KEYS = {"constraints", "labels", "env", "healthChecks", "upgradeStrategy"}

def dispatch(operations, user, request_app, app,
             filters_pipeline=FILTERS_PIPELINE[FilterType.REQUEST]) -> SieveMarathonApp:
    """
    :type operations: Iterable[OperationType]
    :type request_app: MarathonApp
    :type app: MarathonApp
    :type filters_pipeline: Dict[OperationType, Iterable[BaseFilter]]

    todo: (user, request_app, app) podem ser refatorados em uma classe de domínio
    """
    merged_app = merge_marathon_apps(base_app=app, modified_app=request_app)
    for operation in operations:
        for filter_ in filters_pipeline[operation]:
            func = getattr(filter_, operation.value)
            merged_app = func(user, merged_app, app)

    return merged_app


def dispatch_response_pipeline(user, response: Response, filters_pipeline=FILTERS_PIPELINE[FilterType.RESPONSE]) -> FlaskResponse:
    if response.is_app_request():
        filtered_response_apps = []
        for response_app, original_app in response.split():
            filtered_app = response_app
            for filter_ in filters_pipeline:
                if hasattr(filter_, "response"):
                    filtered_app = filter_.response(user, filtered_app, original_app)

            if original_app.id.startswith("/{}/".format(user.current_account.namespace)):
                filtered_response_apps.append((filtered_app, original_app))

        return response.join(filtered_response_apps)
    elif response.is_group_request():
        filtered_response_groups = []
        for response_group, original_group in response.split():
            filtered_group = response_group
            for filter_ in filters_pipeline:
                if hasattr(filter_, "response_group"):
                    filtered_group = filter_.response_group(user, filtered_group, original_group)
            filtered_response_groups.append((filtered_group, original_group))
        return response.join(filtered_response_groups)
    elif response.is_deployment():
        content = json.loads(response.response.data)
        deployments = (MarathonDeployment.from_json(deploy) for deploy in content)

        filtered_deployments = []
        for deployment in deployments:
            for filter_ in filters_pipeline:
                if hasattr(filter_, "response_deployment"):
                    filter_.response_deployment(user, deployment)
            filtered_deployments.append(deployment)

        return FlaskResponse(
            response=json.dumps(filtered_deployments, cls=Response.json_encoder),
            status=response.response.status,
            headers=response.response.headers
        )
    elif response.is_queue_request():
        queue_data = json.loads(response.response.data)
        current_namespace = user.current_account.namespace
        filtered_queue_data = []
        queued_apps = (MarathonQueueItem.from_json(queue_item) for queue_item in queue_data['queue'])
        for queued_app in queued_apps:
            if queued_app.app.id.startswith("/{}".format(current_namespace)):
                queued_app.app.id = queued_app.app.id.replace("/{}".format(current_namespace), "")
                filtered_queue_data.append(queued_app)

        return FlaskResponse(
            response=json.dumps({"queue": filtered_queue_data}, cls=Response.json_encoder),
            status=response.response.status,
            headers=response.response.headers
        )


def merge_marathon_apps(base_app, modified_app):
    """
    A junção das duas apps (request_app (aqui modified_app) e original_app (aqui base_app)) é
    sempre feita pegando todos os dados da original_app e jogando os dados da requst_app "em cima".
    Não podemos usar o `minimal=Fase` na request_app pois para requests que estão *incompletos*, ou seja,
    sem alguns vampos (já veremos exemplo) se esássemos minimal=False, iríramos apagar esses "campos faltantes"
    da original_app. Exemplos:

        request_app = {"instances": 10}
        original_app está completa, com envs, constraints e tudo mais.

        se usamos `minimal=False` na request_app, teremos um JSON com *todos* os campos em branco, menos o "instances".
        Então quando fizermos `merged.update(modified_app.json_repr(minimal=False))`, vamos no final ter um JSON apenas com
        o campo "instances" perrnchido e todo o restante vazio.


    """
    merged = base_app.json_repr(minimal=False)
    merged.update(modified_app.json_repr(minimal=True))
    try:
        raw_request_data = json.loads(request.data)
        for key in REMOVABLE_KEYS:
            if key in raw_request_data:
                merged[key] = raw_request_data[key]
    except Exception as e:
        pass
    return SieveMarathonApp.from_json(merged)

