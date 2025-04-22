from unittest.mock import Mock

from invoke.context import Context

import infrablocks.invoke_terraform.task_factory as task_factory
import infrablocks.invoke_terraform.terraform as tf


class TerraformFactory(task_factory.TerraformFactory):
    def __init__(self, terraform: Mock):
        self._terraform = terraform

    def build(self, context: Context) -> tf.Terraform:
        return self._terraform
