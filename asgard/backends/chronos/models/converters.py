from typing import List

from asgard.backends.models.converters import ModelConverterInterface
from asgard.clients.chronos.models.job import (
    ChronosJob,
    ChronosContainerParameterSpec,
    ChronosContainerVolumeSpec,
    ChronosContainerSpec,
    ChronosEnvSpec,
    ChronosFetchURLSpec,
)
from asgard.models.job import ScheduledJob
from asgard.models.spec.container import (
    ContainerSpec,
    ContainerParameterSpec,
    ContainerVolumeSpec,
)
from asgard.models.spec.env import EnvSpec
from asgard.models.spec.fetch import FetchURLSpec
from asgard.models.spec.schedule import ScheduleSpec


class ChronosScheduledJobConverter(
    ModelConverterInterface[ScheduledJob, ChronosJob]
):
    @classmethod
    def to_asgard_model(cls, other: ChronosJob) -> ScheduledJob:
        if other.environmentVariables:
            env_dict = ChronosEnvSpecConverter.to_asgard_model(
                other.environmentVariables
            )

        if other.fetch:
            fetch_list = ChronosFetchURLSpecConverter.to_asgard_model(
                other.fetch
            )
        return ScheduledJob(
            type="CHRONOS",
            id=other.name,
            description=other.description,
            command=other.command,
            arguments=other.arguments,
            cpus=other.cpus,
            mem=other.mem,
            pull_image=other.container.forcePullImage,
            enabled=not other.disabled,
            shell=other.shell,
            container=ChronosContainerSpecConverter.to_asgard_model(
                other.container
            ),
            schedule=ScheduleSpec(
                value=other.schedule, tz=other.scheduleTimeZone
            ),
            env=env_dict,
            fetch=fetch_list,
        )

    @classmethod
    def to_client_model(cls, other: ScheduledJob) -> ChronosJob:
        pass


class ChronosContainerParameterSpecConverter(
    ModelConverterInterface[
        ContainerParameterSpec, ChronosContainerParameterSpec
    ]
):
    @classmethod
    def to_asgard_model(
        cls, other: ChronosContainerParameterSpec
    ) -> ContainerParameterSpec:
        return ContainerParameterSpec(name=other.key, value=other.value)

    @classmethod
    def to_client_model(
        cls, other: ContainerParameterSpec
    ) -> ChronosContainerParameterSpec:
        return ChronosContainerParameterSpec(key=other.name, value=other.value)


class ChronosContainerVolumeSpecConverter(
    ModelConverterInterface[ContainerVolumeSpec, ChronosContainerVolumeSpec]
):
    @classmethod
    def to_asgard_model(
        cls, other: ChronosContainerVolumeSpec
    ) -> ContainerVolumeSpec:
        return ContainerVolumeSpec(
            container_path=other.containerPath,
            host_path=other.hostPath,
            mode=other.mode,
        )

    @classmethod
    def to_client_model(
        cls, other: ContainerVolumeSpec
    ) -> ChronosContainerVolumeSpec:
        return ChronosContainerVolumeSpec(
            hostPath=other.host_path,
            containerPath=other.container_path,
            mode=other.mode,
        )


class ChronosContainerSpecConverter(
    ModelConverterInterface[ContainerSpec, ChronosContainerSpec]
):
    @classmethod
    def to_asgard_model(cls, other: ChronosContainerSpec) -> ContainerSpec:
        if other.parameters:
            params = [
                ChronosContainerParameterSpecConverter.to_asgard_model(p)
                for p in other.parameters
            ]
        if other.volumes:
            volumes = [
                ChronosContainerVolumeSpecConverter.to_asgard_model(v)
                for v in other.volumes
            ]
        return ContainerSpec(
            type="DOCKER",
            image=other.image,
            network=other.network,
            parameters=params,
            pull_image=other.forcePullImage,
            volumes=volumes,
        )

    @classmethod
    def to_client_model(cls, other: ContainerSpec) -> ChronosContainerSpec:
        if other.parameters:
            params = [
                ChronosContainerParameterSpecConverter.to_client_model(p)
                for p in other.parameters
            ]
        if other.volumes:
            volumes = [
                ChronosContainerVolumeSpecConverter.to_client_model(v)
                for v in other.volumes
            ]
        return ChronosContainerSpec(
            image=other.image,
            network=other.network,
            parameters=params,
            forcePullImage=other.pull_image,
            volumes=volumes,
        )


class ChronosEnvSpecConverter(
    ModelConverterInterface[EnvSpec, List[ChronosEnvSpec]]
):
    @classmethod
    def to_asgard_model(cls, other: List[ChronosEnvSpec]) -> EnvSpec:
        env_dict: EnvSpec = {}
        for other_item in other:
            env_dict[other_item.key] = other_item.value
        return env_dict

    @classmethod
    def to_client_model(cls, other: EnvSpec) -> List[ChronosEnvSpec]:
        env_spec_list: List[ChronosEnvSpec] = []
        for key, value in other.items():
            env_spec_list.append(ChronosEnvSpec(key=key, value=value))

        return env_spec_list


class ChronosFetchURLSpecConverter(
    ModelConverterInterface[List[FetchURLSpec], List[ChronosFetchURLSpec]]
):
    @classmethod
    def to_asgard_model(
        cls, other: List[ChronosFetchURLSpec]
    ) -> List[FetchURLSpec]:
        fetch_list: List[FetchURLSpec] = []
        for fetch_item in other:
            fetch_list.append(
                FetchURLSpec(
                    type="ASGARD",
                    uri=fetch_item.uri,
                    executable=fetch_item.executable,
                    cache=fetch_item.cache,
                    extract=fetch_item.extract,
                )
            )
        return fetch_list

    @classmethod
    def to_client_model(
        cls, other: List[FetchURLSpec]
    ) -> List[ChronosFetchURLSpec]:
        fetch_list: List[ChronosFetchURLSpec] = []
        for fetch_item in other:
            fetch_list.append(
                ChronosFetchURLSpec(
                    uri=fetch_item.uri,
                    executable=fetch_item.executable,
                    cache=fetch_item.cache,
                    extract=fetch_item.extract,
                )
            )
        return fetch_list
