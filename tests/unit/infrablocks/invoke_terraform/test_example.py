from infrablocks.invoke_terraform.example import Example


class TestExample:
    def test_example(self):
        example = Example()
        assert example.example() == 1
