from unittest.mock import Mock

from invoke.context import Context

from infrablocks.invoke_terraform.invoke_executor import InvokeExecutor


class TestInvokeExecutor:
    def test_run_invoked_with_command(self):
        context = Mock(spec=Context)

        executor = InvokeExecutor(context)

        executor.execute(["some_command", "arg1", "arg2"])

        context.run.assert_called_once_with(
            "some_command arg1 arg2",
            env={},
        )

    def test_run_invoked_with_env(self):
        context = Mock(spec=Context)

        executor = InvokeExecutor(context)

        executor.execute(
            ["some_command", "arg1", "arg2"], env={"ENV_VAR": "value"}
        )

        context.run.assert_called_once_with(
            "some_command arg1 arg2",
            env={"ENV_VAR": "value"},
        )

    def test_run_invoked_with_empty_env(self):
        context = Mock(spec=Context)

        executor = InvokeExecutor(context)

        executor.execute(["some_command", "arg1", "arg2"], env=None)

        context.run.assert_called_once_with(
            "some_command arg1 arg2",
            env={},
        )
