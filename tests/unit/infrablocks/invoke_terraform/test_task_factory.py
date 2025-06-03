from io import StringIO
from typing import cast
from unittest.mock import Mock

from invoke.context import Context
from invoke.tasks import Task

from infrablocks.invoke_terraform import (
    Configuration,
    TaskFactory,
    parameter,
    parameters,
)
from infrablocks.invoke_terraform.terraform import (
    BackendConfig,
    Result,
    Terraform,
    Variables,
)
from tests.unit.infrablocks.invoke_terraform.test_support import (
    TerraformFactory,
)


def get_parameters(
        task: Task
) -> list[dict[str, str | int | float | bool]]:
    return [
        {
            "name": argument.name,
            "default": argument.default,
            "help": argument.help,
        }
        for argument in task.get_arguments()
    ]


class TestTaskFactory:
    def test_correctly_names_collection(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.name == "collection"

    def test_adds_all_parameters_to_all_tasks(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            all=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        plan_parameters = get_parameters(collection.tasks["plan"])
        apply_parameters = get_parameters(collection.tasks["apply"])
        output_parameters = get_parameters(collection.tasks["output"])

        assert plan_parameters == apply_parameters == output_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
        ]

    def test_creates_plan_task(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.tasks["plan"] is not None

    def test_adds_only_plan_parameters_to_plan_task(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            plan=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        plan_parameters = get_parameters(collection.tasks["plan"])

        assert plan_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
        ]

    def test_adds_both_all_and_plan_parameters_to_plan_task(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            all=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
            plan=[
                parameter(name="baz", help="Baz parameter", default=True),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        plan_parameters = get_parameters(collection.tasks["plan"])

        assert plan_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
            {"name": "baz", "default": True, "help": "Baz parameter"},
        ]

    def test_plan_does_not_use_workspace_when_not_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = "/some/path"
            configuration.workspace = None

        collection = task_factory.create("collection", [], pre_task_function)
        plan: Task = cast(Task, collection.tasks["plan"])

        plan(Context())

        terraform.select_workspace.assert_not_called()

    def test_plan_uses_workspace_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        collection = task_factory.create("collection", [], pre_task_function)
        plan: Task = cast(Task, collection.tasks["plan"])

        plan(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_plan_initialises_with_reconfigure(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.init_configuration.reconfigure = True

        collection = task_factory.create("collection", [], pre_task_function)
        plan: Task = cast(Task, collection.tasks["plan"])

        plan(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config={},
            reconfigure=True,
            environment={},
        )

    def test_plan_invokes_init_and_plan(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"
        variables: Variables = {"foo": 1}
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.init_configuration.backend_config = backend_config

        collection = task_factory.create("collection", [], pre_task_function)
        plan: Task = cast(Task, collection.tasks["plan"])

        plan(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config=backend_config,
            reconfigure=False,
            environment={},
        )
        terraform.plan.assert_called_once_with(
            chdir=source_directory, vars=variables, environment={}
        )

    def test_plan_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        collection = task_factory.create("collection", [], pre_task_function)
        plan: Task = cast(Task, collection.tasks["plan"])

        plan(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config={},
            reconfigure=False,
            environment=environment,
        )

        terraform.select_workspace.assert_called_once_with(
            "workspace",
            chdir=source_directory,
            or_create=True,
            environment=environment,
        )

        terraform.plan.assert_called_once_with(
            chdir=source_directory, vars={}, environment=environment
        )

    def test_creates_apply_task(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.tasks["apply"] is not None

    def test_adds_only_apply_parameters_to_apply_task(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            apply=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        apply_parameters = get_parameters(collection.tasks["apply"])

        assert apply_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
        ]

    def test_adds_both_all_and_apply_parameters_to_apply_task(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            all=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
            apply=[
                parameter(name="baz", help="Baz parameter", default=True),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        apply_parameters = get_parameters(collection.tasks["apply"])

        assert apply_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
            {"name": "baz", "default": True, "help": "Baz parameter"},
        ]

    def test_apply_invokes_init_and_apply(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"
        variables: Variables = {"foo": 1}
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.init_configuration.backend_config = backend_config

        collection = task_factory.create("collection", [], pre_task_function)
        apply: Task = cast(Task, collection.tasks["apply"])

        apply(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config=backend_config,
            reconfigure=False,
            environment={},
        )
        terraform.apply.assert_called_once_with(
            chdir=source_directory,
            vars=variables,
            autoapprove=True,
            environment={},
        )

    def test_apply_uses_workspace(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        collection = task_factory.create("collection", [], pre_task_function)
        apply: Task = cast(Task, collection.tasks["apply"])

        apply(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_apply_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        collection = task_factory.create("collection", [], pre_task_function)
        apply: Task = cast(Task, collection.tasks["apply"])

        apply(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config={},
            reconfigure=False,
            environment=environment,
        )

        terraform.select_workspace.assert_called_once_with(
            "workspace",
            chdir=source_directory,
            or_create=True,
            environment=environment,
        )

        terraform.apply.assert_called_once_with(
            chdir=source_directory,
            vars={},
            autoapprove=True,
            environment=environment,
        )

    def test_creates_output_task(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.tasks["output"] is not None

    def test_adds_only_output_parameters_to_output_task(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            output=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        output_parameters = get_parameters(collection.tasks["output"])

        assert output_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
        ]

    def test_adds_both_all_and_output_parameters_to_output_task(self):
        pre_task_function_mock = Mock()

        task_parameters = parameters(
            all=[
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            ],
            output=[
                parameter(name="baz", help="Baz parameter", default=True),
            ],
        )

        collection = TaskFactory().create(
            "collection", task_parameters, pre_task_function_mock
        )

        output_parameters = get_parameters(collection.tasks["output"])

        assert output_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
            {"name": "baz", "default": True, "help": "Baz parameter"},
        ]

    def test_output_invokes_init_and_output(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.init_configuration.backend_config = backend_config

        collection = task_factory.create("collection", [], pre_task_function)
        output: Task = cast(Task, collection.tasks["output"])

        output(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config=backend_config,
            reconfigure=False,
            environment={},
        )
        terraform.output.assert_called_once_with(
            chdir=source_directory,
            capture=None,
            json=False,
            environment={},
        )

    def test_output_uses_workspace(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        collection = task_factory.create("collection", [], pre_task_function)
        output: Task = cast(Task, collection.tasks["output"])

        output(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_output_uses_json(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace
            configuration.output_configuration.json = True

        collection = task_factory.create("collection", [], pre_task_function)
        output: Task = cast(Task, collection.tasks["output"])

        output(Context())

        terraform.output.assert_called_once_with(
            chdir=source_directory,
            capture=None,
            json=True,
            environment={},
        )

    def test_output_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        collection = task_factory.create("collection", [], pre_task_function)
        output: Task = cast(Task, collection.tasks["output"])

        output(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config={},
            reconfigure=False,
            environment=environment,
        )

        terraform.select_workspace.assert_called_once_with(
            "workspace",
            chdir=source_directory,
            or_create=True,
            environment=environment,
        )

        terraform.output.assert_called_once_with(
            chdir=source_directory,
            capture=None,
            json=False,
            environment=environment,
        )

    def test_output_returns_standard_output_when_capture_stdout_true(self):
        terraform = Mock(spec=Terraform)
        task_factory = TaskFactory(
            terraform_factory=TerraformFactory(terraform)
        )
        source_directory = "/some/path"

        terraform.output.return_value = Result(
            stdout=StringIO("output_value\n"), stderr=None
        )

        def pre_task_function(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.capture_stdout = True

        collection = task_factory.create("collection", [], pre_task_function)
        output: Task = cast(Task, collection.tasks["output"])

        output_value = output(Context())

        assert output_value == "output_value"
