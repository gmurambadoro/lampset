class Command:
    """Simple class to represent a shell commands"""

    def __init__(self, name: str):
        args = name.split(' ')
        self._name = args[0]
        self._args = args[1] or None

    def __str__(self) -> str:
        return " ".join(self.arguments())

    def arguments(self) -> list:
        args = [self._name]

        if self._args:
            args.append(self._args)

        return args

    def exec(self) -> bool:
        pass

    def exec_with_output(self, suppress_error: bool = False) -> str:
        pass
