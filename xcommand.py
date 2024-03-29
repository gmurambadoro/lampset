import os
import subprocess


class XCommand:
    """Simple class to represent a shell commands"""

    def __init__(self, name: str):
        args, *rest = name.split(' ')
        self._name = str(args or '')
        self._args = " ".join(rest or [])

    def __str__(self) -> str:
        return " ".join(self.arguments())

    def arguments(self) -> list:
        args = [self._name]

        if self._args:
            args.append(self._args)

        return args

    def exec(self, suppress_error=False) -> bool:
        success = os.system(str(self)) == 0

        if not success and not suppress_error:
            raise RuntimeError(f"Error when running command {self}")

        return success

    def exec_with_output(self, suppress_error: bool = False) -> str:
        res = subprocess.run(self.arguments(), subprocess.PIPE)

        if not suppress_error and res.returncode != 0:
            raise RuntimeError(f"Error when running command {self}")

        return str(res.stdout)

    @classmethod
    def run(cls, command: str, suppress_error: False) -> int:
        _command = XCommand(command)
        return _command.exec(suppress_error=suppress_error)


