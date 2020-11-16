import os
import subprocess
import sys


def exec_command(cmd: str, args: str = '') -> bool:
    """Runs the os system command and returns the execution success"""
    run_args = [cmd]

    if args:
        run_args.append(args)

    res = subprocess.run(run_args, stdout=subprocess.PIPE)

    return int(res.returncode) == 0


def exec_command_with_output(cmd: str, args: str = '') -> str:
    run_args = [cmd]

    if args:
        run_args.append(args)

    _res = subprocess.run(run_args, subprocess.PIPE)

    if _res.returncode != 0:
        raise RuntimeError('E: Command Failed: ' + str(_res.stderr))

    return str(_res.stdout)


# upgrade the system
def do_system_upgrade() -> bool:
    return exec_command('sudo apt update && sudo apt upgrade -y')


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
