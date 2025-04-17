from unittest.mock import Mock

from infrablocks.invoke_terraform.task_factory import define_tasks


class TestTaskFactory:
    def test_correctly_names_collection(self):
        pre_task_function_mock = Mock()

        collection = define_tasks("collection", [], pre_task_function_mock)

        assert collection.name == "collection"
