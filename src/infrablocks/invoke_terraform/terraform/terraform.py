from typing import Dict, Iterable, List, Optional, Union

type ConfigurationValue = Union[bool, int, float, str, None]
type Variables = Dict[str, ConfigurationValue]
type BackendConfig = Union[str, Dict[str, ConfigurationValue]]


class Executor:
    def execute(self, command: Iterable[str]) -> None:
        raise Exception("NotImplementedException")


class Terraform:
    def __init__(self, executor: Executor):
        self._executor = executor

    def init(
        self,
        chdir: Optional[str] = None,
        backend_config: Optional[BackendConfig] = {},
        reconfigure: Optional[bool] = False,
    ):
        base_command = self._build_base_command(chdir)
        command = (
            base_command
            + ["init"]
            + self._build_backend_config(backend_config)
        )

        if reconfigure:
            command = command + ["-reconfigure"]

        self._executor.execute(command)

    def plan(
        self, chdir: Optional[str] = None, vars: Optional[Variables] = {}
    ):
        base_command = self._build_base_command(chdir)
        command = base_command + ["plan"] + self._build_vars(vars)

        self._executor.execute(command)

    def apply(
        self, chdir: Optional[str] = None, vars: Optional[Variables] = {}
    ):
        base_command = self._build_base_command(chdir)
        command = base_command + ["apply"] + self._build_vars(vars)

        self._executor.execute(command)

    def select_workspace(
        self,
        workspace: str,
        chdir: Optional[str] = None,
        or_create: bool = False,
    ):
        base_command = self._build_base_command(chdir)
        command = base_command + ["workspace", "select"]

        if or_create:
            command = command + ["-or-create=true"]

        command = command + [workspace]

        self._executor.execute(command)

    @staticmethod
    def _build_base_command(chdir: Optional[str]) -> List[str]:
        command = ["terraform"]

        if chdir is not None:
            return command + [f"-chdir={chdir}"]

        return command

    def _build_vars(self, variables: Optional[Variables]) -> List[str]:
        if not variables:
            return []

        return [
            self._format_configuration_value("-var", key, value)
            for key, value in variables.items()
        ]

    @staticmethod
    def _format_configuration_value(
        option_key: str, key: str, value: ConfigurationValue
    ) -> str:
        if isinstance(value, bool):
            return f'{option_key}="{key}={str(value).lower()}"'
        elif isinstance(value, (int, float)):
            return f'{option_key}="{key}={value}"'
        elif isinstance(value, str):
            return f'{option_key}="{key}={value}"'
        elif value is None:
            return f'{option_key}="{key}=null"'

        raise Exception(
            f"variable with value of type {type(value)} is not supported"
        )

    def _build_backend_config(
        self, backend_config: Optional[BackendConfig]
    ) -> List[str]:
        if not backend_config:
            return []

        if isinstance(backend_config, str):
            return [f"-backend-config={backend_config}"]
        else:
            return [
                self._format_configuration_value("-backend-config", key, value)
                for key, value in backend_config.items()
            ]
