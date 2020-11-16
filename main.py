import os
import subprocess
import sys

from command import Command


try:
    # check if the platform is supported
    if sys.platform != 'linux':
        print(f'E: Your `{sys.platform}` platform is not supported. At the moment we support only `linux` which is '
              f'found in Ubuntu-based Linux distributions.')

        sys.exit(1)

    Command.run('sudo apt update', suppress_error=False)
    Command.run('sudo apt upgrade -y', suppress_error=False)

except RuntimeError as e:
    print()
    print(e)
