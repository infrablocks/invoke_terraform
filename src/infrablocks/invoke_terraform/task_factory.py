from typing import Callable

from invoke.collection import Collection
from invoke.context import Context

import infrablocks.invoke_factory as invoke_factory
import infrablocks.invoke_terraform.terraform as terraform

type PreTaskFunction = Callable[
    [Context, invoke_factory.Arguments, terraform.Configuration], None
]


def define_tasks(
    collection_name: str,
    task_parameters: invoke_factory.Parameters,
    pre_task_function: PreTaskFunction,
):
    col = Collection(collection_name)

    col.add_task(
        invoke_factory.create_task(
            _create_plan(pre_task_function),
            task_parameters,
        )
    )

    col.add_task(
        invoke_factory.create_task(
            _create_apply(pre_task_function),
            task_parameters,
        )
    )
    return col


def _create_plan(
    pre_task_function: PreTaskFunction,
) -> invoke_factory.BodyCallable[None]:
    def plan(context: Context, arguments: invoke_factory.Arguments):
        configuration = terraform.Configuration("", {}, {})
        pre_task_function(
            context,
            arguments,
            configuration,
        )
        terraform.plan(context, configuration)

    return plan


def _create_apply(
    pre_task_function: PreTaskFunction,
) -> invoke_factory.BodyCallable[None]:
    def apply(context: Context, arguments: invoke_factory.Arguments):
        configuration = terraform.Configuration("", {}, {})
        pre_task_function(
            context,
            arguments,
            configuration,
        )
        print("TODO implement apply")

    return apply
