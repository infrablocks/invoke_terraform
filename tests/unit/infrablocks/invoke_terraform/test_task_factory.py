from io import StringIO
from typing import Any
from unittest.mock import Mock

from invoke.context import Context
from invoke.tasks import Task

from infrablocks.invoke_terraform import (
    Configuration,
    TerraformTaskFactory,
)
from infrablocks.invoke_terraform.terraform import (
    BackendConfig,
    Result,
    Terraform,
    Variables,
)
from tests.unit.infrablocks.invoke_terraform.test_support import (
    MockTerraformFactory,
)


def get_parameters(task: Task | None) -> list[dict[str, Any]]:
    if task is None:
        raise ValueError("Task cannot be None")

    return [
        {
            "name": argument.name,
            "default": argument.default,
            "help": argument.help,
        }
        for argument in task.get_arguments()
    ]


class TestTaskFactory:
    def test_plan_does_not_use_workspace_when_not_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = "/some/path"
            configuration.workspace = None

        plan = task_factory.create_plan_task(configure, [])

        plan(Context())

        terraform.select_workspace.assert_not_called()

    def test_plan_uses_workspace_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        plan = task_factory.create_plan_task(configure, [])

        plan(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_plan_initialises_with_reconfigure(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.init.reconfigure = True

        plan = task_factory.create_plan_task(configure, [])

        plan(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config={},
            reconfigure=True,
            environment={},
        )

    def test_plan_invokes_init_and_plan(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        variables: Variables = {"foo": 1}
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.init.backend_config = backend_config

        plan = task_factory.create_plan_task(configure, [])

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
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        plan = task_factory.create_plan_task(configure, [])

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

    def test_apply_invokes_init_and_apply(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        variables: Variables = {"foo": 1}
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.init.backend_config = backend_config

        apply = task_factory.create_apply_task(configure, [])

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
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        apply = task_factory.create_apply_task(configure, [])

        apply(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_apply_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        apply = task_factory.create_apply_task(configure, [])

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

    def test_destroy_invokes_init_and_destroy(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        variables: Variables = {"foo": 1}
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.init.backend_config = backend_config

        destroy = task_factory.create_destroy_task(configure, [])

        destroy(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config=backend_config,
            reconfigure=False,
            environment={},
        )
        terraform.destroy.assert_called_once_with(
            chdir=source_directory,
            vars=variables,
            autoapprove=True,
            environment={},
        )

    def test_destroy_uses_workspace(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        destroy = task_factory.create_destroy_task(configure, [])

        destroy(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_destroy_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        destroy = task_factory.create_destroy_task(configure, [])

        destroy(Context())

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

        terraform.destroy.assert_called_once_with(
            chdir=source_directory,
            vars={},
            autoapprove=True,
            environment=environment,
        )

    def test_validate_invokes_init_and_validate(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.init.backend_config = backend_config

        validate = task_factory.create_validate_task(configure, [])

        validate(Context())

        terraform.init.assert_called_once_with(
            chdir=source_directory,
            backend_config=backend_config,
            reconfigure=False,
            environment={},
        )
        terraform.validate.assert_called_once_with(
            chdir=source_directory,
            json=False,
            environment={},
        )

    def test_validate_uses_workspace(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        validate = task_factory.create_validate_task(configure, [])

        validate(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_validate_uses_json(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace
            configuration.validate.json = True

        validate = task_factory.create_validate_task(configure, [])

        validate(Context())

        terraform.validate.assert_called_once_with(
            chdir=source_directory,
            json=True,
            environment={},
        )

    def test_validate_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        validate = task_factory.create_validate_task(configure, [])

        validate(Context())

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

        terraform.validate.assert_called_once_with(
            chdir=source_directory,
            json=False,
            environment=environment,
        )

    def test_output_invokes_init_and_output(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        backend_config: BackendConfig = {"path": "state_file.tfstate"}

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.init.backend_config = backend_config

        output = task_factory.create_output_task(configure, [])

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
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace

        output = task_factory.create_output_task(configure, [])

        output(Context())

        terraform.select_workspace.assert_called_once_with(
            workspace, chdir=source_directory, or_create=True, environment={}
        )

    def test_output_uses_json(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        workspace = "workspace"
        source_directory = "/some/path"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.workspace = workspace
            configuration.output.json = True

        output = task_factory.create_output_task(configure, [])

        output(Context())

        terraform.output.assert_called_once_with(
            chdir=source_directory,
            capture=None,
            json=True,
            environment={},
        )

    def test_output_uses_environment_in_all_commands_when_set(self):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"
        environment = {"ENV_VAR": "value"}
        workspace = "workspace"

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.environment = environment
            configuration.workspace = workspace

        output = task_factory.create_output_task(configure, [])

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
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )
        source_directory = "/some/path"

        terraform.output.return_value = Result(
            stdout=StringIO("output_value\n"), stderr=None
        )

        def configure(_context, _, configuration: Configuration):
            configuration.source_directory = source_directory
            configuration.output.capture_stdout = True

        output = task_factory.create_output_task(configure, [])

        output_value = output(Context())

        assert output_value == "output_value"
