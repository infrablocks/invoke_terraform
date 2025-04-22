from invoke.context import Context

import infrablocks.invoke_terraform.terraform as tf
from infrablocks.invoke_terraform.invoke_executor import InvokeExecutor


class TerraformFactory:
    def build(self, context: Context) -> tf.Terraform:
        return tf.Terraform(InvokeExecutor(context))
