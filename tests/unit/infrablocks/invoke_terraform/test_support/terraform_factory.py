from unittest.mock import Mock

from invoke.context import Context

from infrablocks.invoke_terraform.terraform import Terraform, TerraformFactory


class MockTerraformFactory(TerraformFactory):
    def __init__(self, terraform: Mock):
        self._terraform = terraform

    def build(self, context: Context) -> Terraform:
        return self._terraform
