import sys

from command import Command

try:
    # check if the platform is supported
    if sys.platform != 'linux':
        print(f'E: Your `{sys.platform}` platform is not supported. At the moment we support only `linux` which is '
              f'found in Ubuntu-based Linux distributions.')

        sys.exit(1)

    # upgrade the system first
    Command.run('sudo apt update', False)
    Command.run('sudo apt upgrade -y', False)

    # register required PPAs
    for ppa in ['ppa:ondrej/apache2', 'ppa:ondrej/php']:
        Command.run(f'sudo add-apt-repository {ppa}', False)

    Command.run('sudo apt update -y', False)

    Command.run('sudo apt install -y curl apache2 libapache2-mod-fcgid', False)
    Command.run('sudo apt install -y mysql-server mysql-client', False)

    # install multiple php versions
    for ver in ['5.6', '7.1', '7.2', '7.3', '7.4']:
        php_extensions = '{PHP_VER} {PHP_VER}-cli {PHP_VER}-common {PHP_VER}-curl {PHP_VER}-gd {PHP_VER}-mbstring ' \
                         '{PHP_VER}-zip {PHP_VER}-xml {PHP_VER}-sqlite3 {PHP_VER}-mysql {PHP_VER}-apcu ' \
                         '{PHP_VER}-fpm libapache2-mod-{PHP_VER}'.replace('{PHP_VER}', 'php' + ver)

        Command.run('sudo apt install -y ' + php_extensions, False)

    # set the default php version
    Command.run('sudo update-alternatives --config php', False)

    # set default apache php to 7.4
    Command.run('sudo a2dismod php5.6', False)
    Command.run('sudo systemctl restart apache2', False)
    Command.run('sudo a2enmod php7.4', False)
    Command.run('sudo systemctl restart apache2', False)

    # add the current user to the www-data group
    Command.run('sudo usermod -a -G www-data $USER', False)

except RuntimeError as e:
    print()
    print(e)
