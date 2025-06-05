from collections.abc import Sequence
from typing import IO
from unittest.mock import Mock

from infrablocks.invoke_terraform.terraform import (
    BackendConfig,
    Environment,
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
            ["terraform", "init"], environment=None
        )

    def test_init_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.init(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "init"], environment=None
        )

    def test_init_executes_with_backend_config_dictionary(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        backend_config: BackendConfig = {"foo": 1}

        terraform.init(backend_config=backend_config)

        executor.execute.assert_called_once_with(
            ["terraform", "init", '-backend-config="foo=1"'], environment=None
        )

    def test_init_executes_with_backend_config_path(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        backend_config = "/some/config.tfvars"

        terraform.init(backend_config=backend_config)

        executor.execute.assert_called_once_with(
            ["terraform", "init", "-backend-config=/some/config.tfvars"],
            environment=None,
        )

    def test_init_executes_with_reconfigure(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.init(reconfigure=True)

        executor.execute.assert_called_once_with(
            ["terraform", "init", "-reconfigure"], environment=None
        )

    def test_init_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.init(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "init"], environment=environment
        )

    def test_plan_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.plan()

        executor.execute.assert_called_once_with(
            ["terraform", "plan"], environment=None
        )

    def test_plan_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.plan(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "plan"], environment=None
        )

    def test_plan_executes_with_vars(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1}

        terraform.plan(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "plan", '-var="foo=1"'], environment=None
        )

    def test_plan_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.plan(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "plan"], environment=environment
        )

    def test_output_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.output()

        executor.execute.assert_called_once_with(
            ["terraform", "output"], environment=None, stdout=None, stderr=None
        )

    def test_output_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.output(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "output"],
            environment=None,
            stdout=None,
            stderr=None,
        )

    def test_output_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.output(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "output"],
            environment=environment,
            stdout=None,
            stderr=None,
        )

    def test_output_executes_with_json(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.output(json=True)

        executor.execute.assert_called_once_with(
            ["terraform", "output", "-json"],
            environment=None,
            stdout=None,
            stderr=None,
        )

    def test_output_executes_with_raw(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.output(raw=True)

        executor.execute.assert_called_once_with(
            ["terraform", "output", "-raw"],
            environment=None,
            stdout=None,
            stderr=None,
        )

    def test_output_executes_with_name(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.output(name="output_name")

        executor.execute.assert_called_once_with(
            ["terraform", "output", "output_name"],
            environment=None,
            stdout=None,
            stderr=None,
        )

    def test_output_captures_standard_output(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        def write_to_stdout(value: str):
            def side_effect(
                command: Sequence[str],
                environment: Environment | None = None,
                stdout: IO[str] | None = None,
                stderr: IO[str] | None = None,
            ):
                if stdout:
                    stdout.write(value)
                return None

            return side_effect

        executor.execute.side_effect = write_to_stdout('"output_value"\n')

        result = terraform.output(capture={"stdout"})

        assert result.stdout is not None
        assert result.stdout.read() == '"output_value"\n'

    def test_output_captures_standard_error(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        def write_to_stderr(value: str):
            def side_effect(
                command: Sequence[str],
                environment: Environment | None = None,
                stdout: IO[str] | None = None,
                stderr: IO[str] | None = None,
            ):
                if stderr:
                    stderr.write(value)
                return None

            return side_effect

        executor.execute.side_effect = write_to_stderr("Error!\n")

        result = terraform.output(capture={"stderr"})

        assert result.stderr is not None
        assert result.stderr.read() == "Error!\n"

    def test_validate_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.validate()

        executor.execute.assert_called_once_with(
            ["terraform", "validate"], environment=None
        )

    def test_validate_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.validate(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "validate"], environment=None
        )

    def test_validate_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.validate(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "validate"], environment=environment
        )

    def test_validate_executes_with_json(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.validate(json=True)

        executor.execute.assert_called_once_with(
            ["terraform", "validate", "-json"], environment=None
        )

    def test_apply_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.apply()

        executor.execute.assert_called_once_with(
            ["terraform", "apply"], environment=None
        )

    def test_apply_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.apply(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "apply"], environment=None
        )

    def test_apply_executes_with_string_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": "bar"}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=bar"'], environment=None
        )

    def test_apply_executes_with_integer_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=1"'], environment=None
        )

    def test_apply_executes_with_float_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1.2}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=1.2"'], environment=None
        )

    def test_apply_executes_with_boolean_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": True}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=true"'], environment=None
        )

    def test_apply_executes_with_none_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": None}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=null"'], environment=None
        )

    def test_apply_executes_with_list_of_string_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": ["ex", "why", "zed"]}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "apply",
                '-var="foo=[\\"ex\\", \\"why\\", \\"zed\\"]"',
            ],
            environment=None,
        )

    def test_apply_executes_with_list_of_integer_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [1, 2, 3]}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=[1, 2, 3]"'], environment=None
        )

    def test_apply_executes_with_list_of_float_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [1.1, 2.2, 3.3]}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=[1.1, 2.2, 3.3]"'],
            environment=None,
        )

    def test_apply_executes_with_list_of_boolean_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [True, False, True]}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=[true, false, true]"'],
            environment=None,
        )

    def test_apply_executes_with_list_of_none_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [None, None, None]}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo=[null, null, null]"'],
            environment=None,
        )

    def test_apply_executes_with_mapping_of_string_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": "x", "b": "y"}}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "apply",
                '-var="foo={\\"a\\": \\"x\\", \\"b\\": \\"y\\"}"',
            ],
            environment=None,
        )

    def test_apply_executes_with_mapping_of_integer_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": 1, "b": 2}}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo={\\"a\\": 1, \\"b\\": 2}"'],
            environment=None,
        )

    def test_apply_executes_with_mapping_of_float_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": 1.1, "b": 2.2}}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", '-var="foo={\\"a\\": 1.1, \\"b\\": 2.2}"'],
            environment=None,
        )

    def test_apply_executes_with_mapping_of_boolean_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": True, "b": False}}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "apply",
                '-var="foo={\\"a\\": true, \\"b\\": false}"',
            ],
            environment=None,
        )

    def test_apply_executes_with_mapping_of_none_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": True, "b": False}}

        terraform.apply(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "apply",
                '-var="foo={\\"a\\": true, \\"b\\": false}"',
            ],
            environment=None,
        )

    def test_apply_executes_with_autoapprove(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.apply(autoapprove=True)

        executor.execute.assert_called_once_with(
            ["terraform", "apply", "-auto-approve"], environment=None
        )

    def test_apply_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.apply(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "apply"], environment=environment
        )

    def test_destroy_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.destroy()

        executor.execute.assert_called_once_with(
            ["terraform", "destroy"], environment=None
        )

    def test_destroy_executes_with_chdir(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.destroy(chdir="/some/dir")

        executor.execute.assert_called_once_with(
            ["terraform", "-chdir=/some/dir", "destroy"], environment=None
        )

    def test_destroy_executes_with_string_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": "bar"}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=bar"'], environment=None
        )

    def test_destroy_executes_with_integer_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=1"'], environment=None
        )

    def test_destroy_executes_with_float_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": 1.2}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=1.2"'], environment=None
        )

    def test_destroy_executes_with_boolean_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": True}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=true"'], environment=None
        )

    def test_destroy_executes_with_none_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": None}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=null"'], environment=None
        )

    def test_destroy_executes_with_list_of_string_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": ["ex", "why", "zed"]}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "destroy",
                '-var="foo=[\\"ex\\", \\"why\\", \\"zed\\"]"',
            ],
            environment=None,
        )

    def test_destroy_executes_with_list_of_integer_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [1, 2, 3]}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=[1, 2, 3]"'], environment=None
        )

    def test_destroy_executes_with_list_of_float_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [1.1, 2.2, 3.3]}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=[1.1, 2.2, 3.3]"'],
            environment=None,
        )

    def test_destroy_executes_with_list_of_boolean_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [True, False, True]}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=[true, false, true]"'],
            environment=None,
        )

    def test_destroy_executes_with_list_of_none_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": [None, None, None]}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo=[null, null, null]"'],
            environment=None,
        )

    def test_destroy_executes_with_mapping_of_string_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": "x", "b": "y"}}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "destroy",
                '-var="foo={\\"a\\": \\"x\\", \\"b\\": \\"y\\"}"',
            ],
            environment=None,
        )

    def test_destroy_executes_with_mapping_of_integer_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": 1, "b": 2}}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", '-var="foo={\\"a\\": 1, \\"b\\": 2}"'],
            environment=None,
        )

    def test_destroy_executes_with_mapping_of_float_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": 1.1, "b": 2.2}}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "destroy",
                '-var="foo={\\"a\\": 1.1, \\"b\\": 2.2}"',
            ],
            environment=None,
        )

    def test_destroy_executes_with_mapping_of_boolean_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": True, "b": False}}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "destroy",
                '-var="foo={\\"a\\": true, \\"b\\": false}"',
            ],
            environment=None,
        )

    def test_destroy_executes_with_mapping_of_none_var(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        variables: Variables = {"foo": {"a": True, "b": False}}

        terraform.destroy(vars=variables)

        executor.execute.assert_called_once_with(
            [
                "terraform",
                "destroy",
                '-var="foo={\\"a\\": true, \\"b\\": false}"',
            ],
            environment=None,
        )

    def test_destroy_executes_with_autoapprove(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)

        terraform.destroy(autoapprove=True)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy", "-auto-approve"], environment=None
        )

    def test_destroy_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        environment = {"ENV_VAR": "value"}

        terraform.destroy(environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "destroy"], environment=environment
        )

    def test_select_workspace_executes(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"

        terraform.select_workspace(workspace)

        executor.execute.assert_called_once_with(
            ["terraform", "workspace", "select", workspace], environment=None
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
            environment=None,
        )

    def test_select_workspace_executes_with_or_create(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"

        terraform.select_workspace(workspace, or_create=True)

        executor.execute.assert_called_once_with(
            ["terraform", "workspace", "select", "-or-create=true", workspace],
            environment=None,
        )

    def test_select_workspace_executes_with_environment(self):
        executor = Mock(spec=Executor)
        terraform = Terraform(executor)
        workspace = "workspace"
        environment = {"ENV_VAR": "value"}

        terraform.select_workspace(workspace, environment=environment)

        executor.execute.assert_called_once_with(
            ["terraform", "workspace", "select", workspace],
            environment=environment,
        )
