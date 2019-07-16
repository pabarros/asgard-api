from asgard.backends.models.converters import ModelConverterInterface
from asgard.clients.chronos.models.job import (
    ChronosJob,
    ChronosContainerParameterSpec,
    ChronosContainerVolumeSpec,
    ChronosContainerSpec,
)
from asgard.models.job import ScheduledJob
from asgard.models.spec.container import (
    ContainerSpec,
    ContainerParameterSpec,
    ContainerVolumeSpec,
)
from asgard.models.spec.schedule import ScheduleSpec


class ChronosScheduledJobConverter(
    ModelConverterInterface[ScheduledJob, ChronosJob]
):
    @classmethod
    def to_asgard_model(cls, other: ChronosJob) -> ScheduledJob:
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
