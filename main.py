import os
import subprocess
import sys

from command import Command


def shell_exec(command: Command) -> bool:
    """Runs the os system command and returns the execution success"""
    return int(os.system(str(command))) == 0


def shell_exec_with_output(command: Command) -> str:
    _res = subprocess.run(command.arguments(), subprocess.PIPE)

    if _res.returncode != 0:
        raise RuntimeError('E: Command Failed: ' + str(_res.stderr))

    return str(_res.stdout)


# upgrade the system
def do_system_upgrade() -> bool:
    return shell_exec(Command('sudo apt update && sudo apt upgrade -y'))


# register ppas
def register_ppas():
    pass


try:
    # check if the platform is supported
    if sys.platform != 'linux':
        print(f'E: Your `{sys.platform}` platform is not supported. At the moment we support only `linux` which is '
              f'found in Ubuntu-based Linux distributions.')
        sys.exit(1)

    # perform any pending system upgrades first
    if not do_system_upgrade():
        raise RuntimeError('E: do_system_upgrade() failed.')

except RuntimeError as e:
    print(e)
