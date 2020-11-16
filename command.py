import os
import subprocess


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
        return int(os.system(str(self))) == 0

    def exec_with_output(self, suppress_error: bool = False) -> str:
        res = subprocess.run(self.arguments(), subprocess.PIPE)

        if not suppress_error and res.returncode != 0:
            raise RuntimeError(f"Error when running command {self}")

        return str(res.stdout)

    @classmethod
    def run(cls, command: str, suppress_error: False) -> int:
        _command = Command(command)
        success = _command.exec()

        if not success and not suppress_error:
            raise RuntimeError(f'Error when running command {_command}')

        return success
