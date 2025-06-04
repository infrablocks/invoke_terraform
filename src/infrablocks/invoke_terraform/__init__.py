from infrablocks.invoke_factory import parameter

from .task_collection import (
    TerraformTaskCollection,
)
from .task_configuration import (
    Configuration,
    GlobalConfigureFunction,
)
from .task_factory import (
    Parameters,
    TerraformTaskFactory,
    parameters,
)

__all__ = [
    "Configuration",
    "GlobalConfigureFunction",
    "TerraformTaskFactory",
    "TerraformTaskCollection",
    "Parameters",
    "parameter",
    "parameters",
]
