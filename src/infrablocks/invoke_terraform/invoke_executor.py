from typing import Iterable

from invoke.context import Context

import infrablocks.invoke_terraform.terraform as tf
from infrablocks.invoke_terraform.terraform.terraform import Environment


class InvokeExecutor(tf.Executor):
    def __init__(self, context: Context):
        self._context = context

    def execute(
        self, command: Iterable[str], env: Environment | None = None
    ) -> None:
        self._context.run(" ".join(command), env=(env or {}))
