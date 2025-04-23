from dataclasses import dataclass
from typing import Callable

from invoke.collection import Collection
from invoke.context import Context

import infrablocks.invoke_factory as invoke_factory
import infrablocks.invoke_terraform.terraform as tf
from infrablocks.invoke_terraform.terraform_factory import TerraformFactory


@dataclass
class Configuration:
    source_directory: str
    backend_config: tf.BackendConfig
    variables: tf.Variables
    workspace: str

    @staticmethod
    def create_empty():
        return Configuration(
            source_directory="",
            backend_config={},
            variables={},
            workspace="default",
        )


type PreTaskFunction = Callable[
    [Context, invoke_factory.Arguments, Configuration], None
]


class TaskFactory:
    def __init__(self):
        self._terraformFactory = TerraformFactory()

    def create(
        self,
        collection_name: str,
        task_parameters: invoke_factory.Parameters,
        pre_task_function: PreTaskFunction,
    ) -> Collection:
        collection = Collection(collection_name)
        plan_task = invoke_factory.create_task(
            self._create_plan(pre_task_function), task_parameters
        )
        apply_task = invoke_factory.create_task(
            self._create_apply(pre_task_function), task_parameters
        )

        # TODO: investigate type issue
        collection.add_task(plan_task)  # pyright: ignore[reportUnknownMemberType]
        collection.add_task(apply_task)  # pyright: ignore[reportUnknownMemberType]
        return collection

    def _create_plan(
        self,
        pre_task_function: PreTaskFunction,
    ) -> invoke_factory.BodyCallable[None]:
        def plan(context: Context, arguments: invoke_factory.Arguments):
            configuration = Configuration.create_empty()
            pre_task_function(
                context,
                arguments,
                configuration,
            )
            terraform = self._terraformFactory.build(context)
            terraform.init(
                chdir=configuration.source_directory,
                backend_config=configuration.backend_config,
            )
            terraform.select_workspace(
                configuration.workspace,
                chdir=configuration.source_directory,
                or_create=True,
            )
            terraform.plan(
                chdir=configuration.source_directory,
                vars=configuration.variables,
            )

        return plan

    def _create_apply(
        self,
        pre_task_function: PreTaskFunction,
    ) -> invoke_factory.BodyCallable[None]:
        def apply(context: Context, arguments: invoke_factory.Arguments):
            configuration = Configuration.create_empty()
            pre_task_function(
                context,
                arguments,
                configuration,
            )
            terraform = self._terraformFactory.build(context)
            terraform.init(
                chdir=configuration.source_directory,
                backend_config=configuration.backend_config,
            )
            terraform.select_workspace(
                configuration.workspace,
                chdir=configuration.source_directory,
                or_create=True,
            )
            terraform.apply(
                chdir=configuration.source_directory,
                vars=configuration.variables,
            )

        return apply
