from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict, cast

from invoke.collection import Collection
from invoke.context import Context

from infrablocks.invoke_factory import (
    Arguments,
    BodyCallable,
    ParameterList,
    create_task,
)
from infrablocks.invoke_terraform.terraform import (
    BackendConfig,
    Environment,
    StreamNames,
    Terraform,
    TerraformFactory,
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
    init_configuration: InitConfiguration
    output_configuration: OutputConfiguration

    source_directory: str
    variables: Variables
    workspace: str | None
    auto_approve: bool = True

    capture_stdout: bool = False
    environment: Environment | None = None

    @staticmethod
    def create_empty():
        return Configuration(
            init_configuration=InitConfiguration(
                backend_config={}, reconfigure=False
            ),
            output_configuration=OutputConfiguration(json=False),
            source_directory="",
            variables={},
            workspace=None,
            capture_stdout=False,
            environment={},
        )


type PreTaskFunction = Callable[[Context, Arguments, Configuration], None]


class ParameterDict(TypedDict):
    all: NotRequired[ParameterList]
    apply: NotRequired[ParameterList]
    plan: NotRequired[ParameterList]
    output: NotRequired[ParameterList]


def parameters(
    all: ParameterList | None = None,
    apply: ParameterList | None = None,
    plan: ParameterList | None = None,
    output: ParameterList | None = None,
) -> ParameterDict:
    dict: ParameterDict = ParameterDict()
    for key, params in [
        ("all", all),
        ("apply", apply),
        ("plan", plan),
        ("output", output),
    ]:
        if params is not None:
            dict[key] = params

    return dict


type Parameters = ParameterList | ParameterDict


class TaskFactory:
    def __init__(
        self, terraform_factory: TerraformFactory = TerraformFactory()
    ):
        self._terraform_factory = terraform_factory

    def create(
        self,
        collection_name: str,
        task_parameters: Parameters,
        pre_task_function: PreTaskFunction,
    ) -> Collection:
        collection = Collection(collection_name)

        plan_task = create_task(
            self._create_plan(pre_task_function),
            self._plan_parameters(task_parameters),
        )
        apply_task = create_task(
            self._create_apply(pre_task_function),
            self._apply_parameters(task_parameters),
        )
        output_task = create_task(
            self._create_output(pre_task_function),
            self._output_parameters(task_parameters),
        )

        # TODO: investigate type issue
        collection.add_task(  # pyright: ignore[reportUnknownMemberType]
            plan_task
        )
        collection.add_task(  # pyright: ignore[reportUnknownMemberType]
            apply_task
        )
        collection.add_task(  # pyright: ignore[reportUnknownMemberType]
            output_task
        )

        return collection

    def _create_plan(
        self,
        pre_task_function: PreTaskFunction,
    ) -> BodyCallable[None]:
        def plan(context: Context, arguments: Arguments):
            (terraform, configuration) = self._pre_command_setup(
                pre_task_function, context, arguments
            )
            terraform.plan(
                chdir=configuration.source_directory,
                vars=configuration.variables,
                environment=configuration.environment,
            )

        return plan

    def _create_apply(
        self,
        pre_task_function: PreTaskFunction,
    ) -> BodyCallable[None]:
        def apply(context: Context, arguments: Arguments):
            (terraform, configuration) = self._pre_command_setup(
                pre_task_function, context, arguments
            )
            terraform.apply(
                chdir=configuration.source_directory,
                vars=configuration.variables,
                autoapprove=configuration.auto_approve,
                environment=configuration.environment,
            )

        return apply

    def _create_output(
        self, pre_task_function: PreTaskFunction
    ) -> BodyCallable[str | None]:
        def output(context: Context, arguments: Arguments) -> str | None:
            (terraform, configuration) = self._pre_command_setup(
                pre_task_function, context, arguments
            )

            capture: StreamNames | None = None
            if configuration.capture_stdout:
                capture = {"stdout"}

            result = terraform.output(
                chdir=configuration.source_directory,
                capture=capture,
                json=configuration.output_configuration.json,
                environment=configuration.environment,
            )

            if configuration.capture_stdout and result.stdout is not None:
                output = result.stdout.read()
                return output.strip()

            return None

        return output

    def _plan_parameters(self, task_parameters: Parameters) -> ParameterList:
        return self._task_parameters(task_parameters, "plan")

    def _apply_parameters(self, task_parameters: Parameters) -> ParameterList:
        return self._task_parameters(task_parameters, "apply")

    def _output_parameters(self, task_parameters: Parameters) -> ParameterList:
        return self._task_parameters(task_parameters, "output")

    def _task_parameters(
        self,
        task_parameters: Parameters,
        task_name: Literal["apply", "plan", "output"],
    ) -> ParameterList:
        if isinstance(task_parameters, dict):
            task_parameters = cast(ParameterDict, task_parameters)
            return [
                *self._lookup_parameters(task_parameters, "all"),
                *self._lookup_parameters(task_parameters, task_name),
            ]
        return task_parameters

    @staticmethod
    def _lookup_parameters(
        task_parameters: ParameterDict,
        task_name: Literal["all", "apply", "plan", "output"],
    ) -> ParameterList:
        parameters = task_parameters.get(task_name, None)
        return parameters if parameters is not None else []

    def _pre_command_setup(
        self,
        pre_task_function: PreTaskFunction,
        context: Context,
        arguments: Arguments,
    ) -> tuple[Terraform, Configuration]:
        configuration = Configuration.create_empty()
        pre_task_function(
            context,
            arguments,
            configuration,
        )
        terraform = self._terraform_factory.build(context)
        terraform.init(
            chdir=configuration.source_directory,
            backend_config=configuration.init_configuration.backend_config,
            reconfigure=configuration.init_configuration.reconfigure,
            environment=configuration.environment,
        )

        if configuration.workspace is not None:
            terraform.select_workspace(
                configuration.workspace,
                chdir=configuration.source_directory,
                or_create=True,
                environment=configuration.environment,
            )

        return terraform, configuration
