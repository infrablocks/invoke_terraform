from collections.abc import Mapping, Sequence

type ConfigurationValue = bool | int | float | str | None
type Variables = Mapping[str, ConfigurationValue]
type BackendConfig = str | Mapping[str, ConfigurationValue]
type Environment = Mapping[str, str]


class Executor:
    def execute(self, command: Sequence[str], env: Environment | None) -> None:
        raise Exception("NotImplementedException")


class Terraform:
    def __init__(self, executor: Executor):
        self._executor = executor

    def init(
        self,
        chdir: str | None = None,
        backend_config: BackendConfig | None = None,
        reconfigure: bool = False,
        environment: Environment | None = None,
    ):
        base_command = self._build_base_command(chdir)
        command = (
            base_command
            + ["init"]
            + self._build_backend_config(backend_config)
        )

        if reconfigure:
            command = command + ["-reconfigure"]

        self._executor.execute(command, env=environment)

    def plan(
        self,
        chdir: str | None = None,
        vars: Variables | None = None,
        environment: Environment | None = None,
    ):
        base_command = self._build_base_command(chdir)
        command = base_command + ["plan"] + self._build_vars(vars)

        self._executor.execute(command, env=environment)

    def apply(
        self,
        chdir: str | None = None,
        vars: Variables | None = None,
        autoapprove: bool = False,
        environment: Environment | None = None,
    ):
        base_command = self._build_base_command(chdir)
        autoapprove_flag = ["-auto-approve"] if autoapprove else []
        command = (
            base_command
            + ["apply"]
            + autoapprove_flag
            + self._build_vars(vars)
        )

        self._executor.execute(command, env=environment)

    def select_workspace(
        self,
        workspace: str,
        chdir: str | None = None,
        or_create: bool = False,
        environment: Environment | None = None,
    ):
        base_command = self._build_base_command(chdir)
        command = base_command + ["workspace", "select"]

        if or_create:
            command = command + ["-or-create=true"]

        command = command + [workspace]

        self._executor.execute(command, env=environment)

    @staticmethod
    def _build_base_command(chdir: str | None) -> list[str]:
        command = ["terraform"]

        if chdir is not None:
            return command + [f"-chdir={chdir}"]

        return command

    def _build_vars(self, variables: Variables | None) -> list[str]:
        if variables is None:
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
        self, backend_config: BackendConfig | None
    ) -> list[str]:
        if backend_config is None:
            return []

        if isinstance(backend_config, str):
            return [f"-backend-config={backend_config}"]
        else:
            return [
                self._format_configuration_value("-backend-config", key, value)
                for key, value in backend_config.items()
            ]
