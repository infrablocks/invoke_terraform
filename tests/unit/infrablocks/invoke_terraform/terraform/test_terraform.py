from unittest.mock import Mock

from infrablocks.invoke_terraform.terraform import (
    BackendConfig,
    Executor,
    Terraform,
    Variables,
)


class TestTerraform:
    def test_terraform_can_be_instantiated(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        assert terraform is not None

    def test_init_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.init()

        executor.execute.assert_called_once_with(
            ["terraform", "init"], env=None
        )

    def test_init_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.init(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "init"], env=None
        )

    def test_init_executes_with_backend_config_dictionary(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        backend_config: BackendConfig = {"foo": 1}

        terraform.init(backend_config=backend_config)

        executor.execute.assert_called_once_with(
            ["terraform", "init", '-backend-config="foo=1"'], env=None
        )

    def test_init_executes_with_backend_config_path(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        backend_config = "/some/config.tfvars"

        terraform.init(backend_config=backend_config)

        executor.execute.assert_called_once_with(
            ["terraform", "init", "-backend-config=/some/config.tfvars"],
            env=None,
        )

    def test_init_executes_with_reconfigure(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.init(reconfigure=True)

        executor.execute.assert_called_once_with(
            ["terraform", "init", "-reconfigure"], env=None
        )

    def test_init_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.init(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "init"], env=environment
        )

    def test_plan_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.plan()

        executor.execute.assert_called_once_with(
            ["terraform", "plan"], env=None
        )

    def test_plan_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.plan(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "plan"], env=None
        )

    def test_plan_executes_with_vars(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1}

        terraform.plan(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "plan", '-var="foo=1"'], env=None
        )

    def test_plan_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.plan(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "plan"], env=environment
        )

    def test_apply_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.apply()

        executor.execute.assert_called_once_with(
            ["terraform", "apply"], env=None
        )

    def test_apply_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.apply(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "apply"], env=None
        )

    def test_apply_executes_with_vars(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=1"'], env=None
        )

    def test_apply_executes_with_autoapprove(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.apply(autoapprove=True)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", "-auto-approve"], env=None
        )

    def test_apply_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.apply(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "apply"], env=environment
        )

    def test_select_workspace_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"

        terraform.select_workspace(workspace)

        executor.execute.assert_called_once_with(
            ["terraform", "workspace", "select", workspace], env=None
        )

    def test_select_workspace_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"

        terraform.select_workspace(workspace, chdir="/some/dir")

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "-chdir=/some/dir",
                "workspace",
                "select",
                workspace,
            ],
            env=None,
        )

    def test_select_workspace_executes_with_or_create(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"

        terraform.select_workspace(workspace, or_create=True)

        executor.execute.assert_called_once_with(
            ["terraform", "workspace", "select", "-or-create=true", workspace],
            env=None,
        )

    def test_select_workspace_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"
        environment = {"ENV_VAR": "value"}

        terraform.select_workspace(workspace, environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "workspace", "select", workspace], env=environment
        )
