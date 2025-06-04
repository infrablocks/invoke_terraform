from typing import Self, TypedDict, Unpack

from invoke.collection import Collection

from infrablocks.invoke_factory import Parameter, ParameterList

from .task_configuration import GlobalConfigureFunction
from .task_factory import TerraformTaskFactory


class TerraformTaskCollectionParameters(TypedDict, total=False):
    configuration_name: str
    global_parameters: ParameterList
    configure_function: GlobalConfigureFunction


class TerraformTaskCollection:
    def __init__(
        self,
        configuration_name: str | None = None,
        global_parameters: ParameterList | None = None,
        configure_function: GlobalConfigureFunction | None = None,
        task_factory: TerraformTaskFactory = TerraformTaskFactory(),
    ):
        self.configuration_name = configuration_name
        self.global_parameters: ParameterList = (
            global_parameters if global_parameters is not None else []
        )
        self.configure_function: GlobalConfigureFunction = (
            configure_function
            if configure_function is not None
            else lambda context, arguments, configuration: None
        )
        self._task_factory = task_factory

    def _clone(
        self, **kwargs: Unpack[TerraformTaskCollectionParameters]
    ) -> Self:
        return self.__class__(
            configuration_name=kwargs.get(
                "configuration_name", self.configuration_name
            ),
            global_parameters=kwargs.get(
                "global_parameters", self.global_parameters
            ),
            configure_function=kwargs.get(
                "configure_function", self.configure_function
            ),
            task_factory=self._task_factory,
        )

    def for_configuration(self, configuration_name: str):
        return self._clone(configuration_name=configuration_name)

    def with_global_parameters(self, *global_parameters: Parameter) -> Self:
        return self._clone(global_parameters=global_parameters)

    def with_global_configure_function(
        self, configure_function: GlobalConfigureFunction
    ) -> Self:
        return self._clone(configure_function=configure_function)

    def create(self) -> Collection:
        collection = Collection(self.configuration_name)

        plan_task = self._task_factory.create_plan_task(
            self.configure_function, self.global_parameters
        )
        apply_task = self._task_factory.create_apply_task(
            self.configure_function, self.global_parameters
        )
        output_task = self._task_factory.create_output_task(
            self.configure_function, self.global_parameters
        )

        collection.add_task(  # pyright: ignore[reportUnknownMemberType]
            plan_task
        )
        collection.add_task(  # pyright: ignore[reportUnknownMemberType]
            apply_task
        )
        collection.add_task(  # pyright: ignore[reportUnknownMemberType]
            output_task
        )

        return collection
