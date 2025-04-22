from typing import cast
from unittest.mock import Mock

from invoke.context import Context
from invoke.tasks import Task

import infrablocks.invoke_terraform.terraform as tf
from infrablocks.invoke_terraform.task_factory import TaskFactory
from tests.unit.infrablocks.invoke_terraform.test_support import (
    TerraformFactory,
)


class TestTaskFactory:
    def test_correctly_names_collection(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.name == "collection"

    def test_creates_plan_task(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.tasks["plan"] is not None

    def test_plan_invokes_init_and_plan(self):
        terraform = Mock(spec=tf.Terraform)
        task_factory = TaskFactory()
        task_factory._terraformFactory = TerraformFactory(terraform)
        source_directory = "/some/path"
        variables: tf.Variables = {"foo": 1}
        backend_config: tf.BackendConfig = {"path": "state_file.tfstate"}

        def pre_task_function(_context, _, configuration: tf.Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.backend_config = backend_config

        collection = task_factory.create("collection", [], pre_task_function)
        plan: Task = cast(Task, collection.tasks["plan"])

        plan(Context())

        terraform.init.assert_called_once()
        terraform.plan.assert_called_once()

    def test_creates_apply_task(self):
        pre_task_function_mock = Mock()

        collection = TaskFactory().create(
            "collection", [], pre_task_function_mock
        )

        assert collection.tasks["apply"] is not None

    def test_apply_invokes_init_and_plan_and_apply(self):
        terraform = Mock(spec=tf.Terraform)
        task_factory = TaskFactory()
        task_factory._terraformFactory = TerraformFactory(terraform)
        source_directory = "/some/path"
        variables: tf.Variables = {"foo": 1}
        backend_config: tf.BackendConfig = {"path": "state_file.tfstate"}

        def pre_task_function(_context, _, configuration: tf.Configuration):
            configuration.source_directory = source_directory
            configuration.variables = variables
            configuration.backend_config = backend_config

        collection = task_factory.create("collection", [], pre_task_function)
        apply: Task = cast(Task, collection.tasks["apply"])

        apply(Context())

        terraform.init.assert_called_once()
        terraform.apply.assert_called_once()
