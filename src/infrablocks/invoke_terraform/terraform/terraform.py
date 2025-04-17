from dataclasses import dataclass
from typing import Dict, Union

from invoke.context import Context

default_work_directory = "build"


type ConfigurationValue = Union[bool, int, float, str, None]
type Variables = Dict[str, ConfigurationValue]
type BackendConfig = Union[str, Dict[str, ConfigurationValue]]


@dataclass
class Configuration:
    source_directory: str
    backend_config: BackendConfig
    variables: Variables


def init(context: Context, configuration: Configuration):
    configuration_directory = _initialize_configuration_directory(
        context, configuration.source_directory
    )
    command = f"terraform -chdir={configuration_directory} init "
    command = _append_backend_config(command, configuration.backend_config)
    context.run(command, echo=True)


def _create_configuration_directory_path(source_directory: str):
    return f"{default_work_directory}/{source_directory}"


def _initialize_configuration_directory(
    context: Context, source_directory: str
) -> str:
    configuration_directory = _create_configuration_directory_path(
        source_directory
    )
    context.run(f"rm -rf {configuration_directory}")
    context.run(f"mkdir -p {configuration_directory}")
    context.run(f"cp -r {source_directory}/. {configuration_directory}")
    return configuration_directory


def _append_backend_config(command: str, backend_config: BackendConfig) -> str:
    if isinstance(backend_config, str):
        return f"{command} -backend-config={backend_config}"
    else:
        for key, value in backend_config.items():
            command += f' -backend-config="{key}={value}"'
        return command


def plan(context: Context, configuration: Configuration):
    _validate_configuration(configuration)
    init(context, configuration)
    command = f"terraform plan -chdir={_create_configuration_directory_path(configuration.source_directory)}"
    command = _append_vars(command, configuration.variables)
    context.run(command, echo=True)


def _append_vars(command: str, variables: Variables) -> str:
    if not variables:
        return command

    for key, value in variables.items():
        if isinstance(value, bool):
            command += f' -var="{key}={str(value).lower()}"'
        elif isinstance(value, (int, float)):
            command += f' -var="{key}={value}"'
        elif isinstance(value, str):
            command += f' -var="{key}={value}"'
        elif value is None:
            command += f' -var="{key}=null"'

    return command


def _validate_configuration(configuration: Configuration):
    if not configuration.source_directory:
        raise Exception("source directory was empty")
