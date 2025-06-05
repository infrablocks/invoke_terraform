from typing import Any, cast
from unittest.mock import Mock

import pytest
from invoke.context import MockContext
from invoke.tasks import Task

from infrablocks.invoke_factory import BodyCallable
from infrablocks.invoke_terraform import (
    TerraformTaskCollection,
    TerraformTaskFactory,
    parameter,
)
from infrablocks.invoke_terraform.terraform import (
    Terraform,
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


class TestTaskCollection:
    def test_correctly_names_collection(self):
        collection = (
            TerraformTaskCollection().for_configuration("collection").create()
        )

        assert collection.name == "collection"

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_creates_task(self, task_name: str):
        collection = (
            TerraformTaskCollection().for_configuration("collection").create()
        )

        assert collection.tasks[task_name] is not None

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_defines_global_parameters_on_task(self, task_name: str):
        collection = (
            TerraformTaskCollection()
            .for_configuration("collection")
            .with_global_parameters(
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            )
            .create()
        )

        task_parameters = get_parameters(collection.tasks[task_name])

        assert task_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
        ]

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_defines_global_configure_function_for_task(self, task_name: str):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )

        def configure(context, arguments, configuration):
            configuration.source_directory = "/some/path"
            configuration.environment = {}
            configuration.init.backend_config = {}
            configuration.init.reconfigure = False

        collection = (
            TerraformTaskCollection(task_factory=task_factory)
            .for_configuration("collection")
            .with_global_configure_function(configure)
            .create()
        )
        task = cast(Task[BodyCallable[Any]], collection.tasks[task_name])

        task(MockContext())

        terraform.init.assert_called_once_with(
            chdir="/some/path",
            backend_config={},
            reconfigure=False,
            environment={},
        )

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_allows_extra_parameters_to_be_defined_for_tasks(self, task_name):
        collection = (
            TerraformTaskCollection()
            .for_configuration("collection")
            .with_global_parameters(
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            )
            .with_extra_task_parameters(
                task_name,
                parameter(name="baz", help="Baz parameter", default=True),
            )
            .create()
        )

        task_parameters = get_parameters(collection.tasks[task_name])

        assert task_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "bar", "default": "twenty", "help": "Bar parameter"},
            {"name": "baz", "default": True, "help": "Baz parameter"},
        ]

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_allows_parameters_to_be_overridden_for_tasks(self, task_name):
        collection = (
            TerraformTaskCollection()
            .for_configuration("collection")
            .with_global_parameters(
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="bar", help="Bar parameter", default="twenty"),
            )
            .with_overridden_task_parameters(
                task_name,
                parameter(name="foo", help="Foo parameter", default=10),
                parameter(name="baz", help="Baz parameter", default=True),
            )
            .create()
        )

        task_parameters = get_parameters(collection.tasks[task_name])

        assert task_parameters == [
            {"name": "foo", "default": 10, "help": "Foo parameter"},
            {"name": "baz", "default": True, "help": "Baz parameter"},
        ]

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_allows_extra_configure_function_to_be_defined_for_tasks(
        self, task_name
    ):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )

        def global_configure(context, arguments, configuration):
            configuration.source_directory = "/some/path"
            configuration.environment = {}
            configuration.init.backend_config = {}
            configuration.init.reconfigure = False

        def task_configure(context, arguments, configuration):
            configuration.environment = {"EXTRA_ENV_VAR": "value"}

        collection = (
            TerraformTaskCollection(task_factory=task_factory)
            .for_configuration("collection")
            .with_global_configure_function(global_configure)
            .with_extra_task_configure_function(task_name, task_configure)
            .create()
        )
        task = cast(Task[BodyCallable[Any]], collection.tasks[task_name])

        task(MockContext())

        terraform.init.assert_called_once_with(
            chdir="/some/path",
            backend_config={},
            reconfigure=False,
            environment={"EXTRA_ENV_VAR": "value"},
        )

    @pytest.mark.parametrize(
        "task_name", ["validate", "plan", "apply", "destroy", "output"]
    )
    def test_allows_configure_function_to_be_overridden_for_tasks(
        self, task_name
    ):
        terraform = Mock(spec=Terraform)
        task_factory = TerraformTaskFactory(
            terraform_factory=MockTerraformFactory(terraform)
        )

        def global_configure(context, arguments, configuration):
            configuration.source_directory = "/some/path"
            configuration.environment = {}
            configuration.init.backend_config = {}
            configuration.init.reconfigure = False

        def task_configure(context, arguments, configuration):
            configuration.source_directory = "/other/path"
            configuration.environment = {"EXTRA_ENV_VAR": "value"}
            configuration.init.backend_config = {}
            configuration.init.reconfigure = True

        collection = (
            TerraformTaskCollection(task_factory=task_factory)
            .for_configuration("collection")
            .with_global_configure_function(global_configure)
            .with_overridden_task_configure_function(task_name, task_configure)
            .create()
        )
        task = cast(Task[BodyCallable[Any]], collection.tasks[task_name])

        task(MockContext())

        terraform.init.assert_called_once_with(
            chdir="/other/path",
            backend_config={},
            reconfigure=True,
            environment={"EXTRA_ENV_VAR": "value"},
        )
