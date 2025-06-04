from collections.abc import Callable
from dataclasses import dataclass

from invoke.context import Context

from infrablocks.invoke_factory import (
    Arguments,
)
from infrablocks.invoke_terraform.terraform import (
    BackendConfig,
    Environment,
    Variables,
)


@dataclass
class InitConfiguration:
    backend_config: BackendConfig
    reconfigure: bool


@dataclass
class OutputConfiguration:
    json: bool


@dataclass
class Configuration:
    init: InitConfiguration
    output: OutputConfiguration

    source_directory: str
    variables: Variables
    workspace: str | None
    auto_approve: bool = True

    capture_stdout: bool = False
    environment: Environment | None = None

    @staticmethod
    def create_empty():
        return Configuration(
            init=InitConfiguration(backend_config={}, reconfigure=False),
            output=OutputConfiguration(json=False),
            source_directory="",
            variables={},
            workspace=None,
            capture_stdout=False,
            environment={},
        )


type GlobalConfigureFunction = Callable[
    [Context, Arguments, Configuration], None
]
