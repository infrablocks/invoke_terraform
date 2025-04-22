from typing import Iterable

from invoke.context import Context

import infrablocks.invoke_terraform.terraform as tf


class InvokeExecutor(tf.Executor):
    def __init__(self, context: Context):
        self._context = context

    def execute(self, command: Iterable[str]) -> None:
        self._context.run(" ".join(command))
