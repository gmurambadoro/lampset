#!/usr/bin/python3
import sys
from getpass import getpass

from command import Command

PHP_VERSIONS = [
    'php8.1',
    'php8.0',
    'php7.4', 
    'php7.2',     
]

PHP_DEFAULT_VERSION = PHP_VERSIONS[0]


def heading(title: str) -> None:
    print()
    print(f"== {title} ==".upper())
    print()


try:
    # check if the platform is supported
    if sys.platform != 'linux':
        print(f'E: Your `{sys.platform}` platform is not supported. At the moment we support only `linux` which is '
              f'found in Ubuntu-based Linux distributions.')

        sys.exit(1)

    heading("System Upgrade")

    # upgrade the system first
    Command.run('sudo apt update', False)
    Command.run('sudo apt upgrade -y', False)

    heading("Registering PPAs")

    # register required PPAs
    for ppa in ['ppa:ondrej/apache2', 'ppa:ondrej/php']:
        Command.run(f'sudo add-apt-repository {ppa} -y', False)

    Command.run('sudo apt update -y', False)

    heading("Installing Apache and MySQL")

    Command.run('sudo apt install -y curl apache2 libapache2-mod-fcgid', False)
    Command.run('sudo apt install -y mysql-server mysql-client', False)

    heading("Installing Multiple PHP Versions")

    # install multiple php versions
    for ver in PHP_VERSIONS:
        php_extensions = '{PHP_VER} {PHP_VER}-cli {PHP_VER}-common {PHP_VER}-curl {PHP_VER}-gd {PHP_VER}-mbstring ' \
                         '{PHP_VER}-zip {PHP_VER}-xml {PHP_VER}-sqlite3 {PHP_VER}-mysql {PHP_VER}-apcu ' \
                         '{PHP_VER}-fpm libapache2-mod-{PHP_VER}'.replace('{PHP_VER}', ver)

        Command.run('sudo apt install -y ' + php_extensions, False)

    # set the default php version
    Command.run('sudo update-alternatives --config php', False)

    heading("Configuring Default PHP Version for Apache")

    # set default apache php to latest php version
    Command.run('sudo a2enmod ' + PHP_DEFAULT_VERSION, True)
    Command.run('sudo systemctl restart apache2', False)

    heading('PHP FPM')

    for ver in PHP_VERSIONS:
        Command.run('sudo systemctl start %s-fpm' % ver, False)

    Command.run('sudo a2enmod actions fcgid alias proxy_fcgi rewrite', False)
    Command.run('sudo systemctl restart apache2', False)

    heading("Setting Up User Permissions")

    # add the current user to the www-data group
    Command.run('sudo usermod -a -G www-data $USER', False)
    Command.run('sudo usermod -a -G vboxsf $USER', True)

    # allow apache2 to have read/write access to virtualbox shared folders
    Command.run('sudo usermod -a -G vboxsf www-data', True)

    print("[OK] Permissions were setup successfully.")

    heading("COMPOSER")

    # @see https://getcomposer.org/doc/faqs/how-to-install-composer-programmatically.md
    Command.run('wget https://raw.githubusercontent.com/composer/getcomposer.org'
                '/76a7060ccb93902cd7576b67264ad91c8a2700e2/web/installer -O - -q | php -- --quiet', False)
    Command.run('chmod +x composer.phar', False)
    Command.run('sudo mv composer.phar /usr/local/bin/composer', False)
    Command.run('composer --version', False)

    heading('SYMFONY')

    Command.run("echo 'deb [trusted=yes] https://repo.symfony.com/apt/ /' | sudo tee /etc/apt/sources.list.d/symfony-cli.list", False)
    Command.run("sudo apt update -y && sudo apt install symfony-cli -y")
    Command.run('symfony -V', False)

    print("LAMPSET VHOST-ADD")
    Command.run('rm -rf /tmp/lampset-vhost-add', True)
    Command.run('git clone https://github.com/gmurambadoro/lampset-vhost-add.git /tmp/lampset-vhost-add', False)
    Command.run('chmod +x /tmp/lampset-vhost-add/lampset-vhost-add.py', False)
    Command.run('sudo mv --force /tmp/lampset-vhost-add/lampset-vhost-add.py /usr/local/bin/vhost-add', False)
    Command.run('vhost-add --help', False)

    heading("Configuring MySQL")

    res = input("""
Do you want to secure your MySQL installation by running `mysql_secure_installation`?

== NB: If already run, please select `N` to skip this part ==

Do yo want want to run `mysql_secure_installation` now (Y/n): """)

    if 'y' == str(res or '').strip().lower():
        Command.run('sudo mysql_secure_installation', False)

    msg = """
If you frequently connect to MySQL via third party clients like Workbench and phpMyAdmin you might run 
into `MySQL Access Denied` issues. 

== NB: If already run, please select `N` to skip this part ==

Do you want to fix the configuration file to allow for clients like Workbench and phpMyAdmin 
to connect to MySQL? (Y/n):  """

    yes = str(input(msg)).strip().lower() == 'y'

    if yes:
        username = str(input('MySQL Username (root): ')).strip()
        password = str(getpass('Password: ')).strip()
        confirm_password = str(getpass('Confirm Password: ')).strip()

        while password != confirm_password:
            print()
            print('!! Passwords do not match. Please try again.')
            print()
            password = str(getpass('Password: ')).strip()
            confirm_password = str(getpass('Confirm Password: ')).strip()

        print()
        print()
        print(f"""
Please enter the following commands manually in the terminal:
mysql> ALTER USER '{username}'@'localhost' IDENTIFIED WITH mysql_native_password BY '{password}';
mysql> FLUSH PRIVILEGES;
mysql> quit
            """)

        Command.run('sudo mysql', True)

    heading("PHP Versions")

    for ver in PHP_VERSIONS:
        Command.run('%s --version' % ver, False)

    heading("Default PHP Version")

    Command.run('php --version', True)

    heading("Software Versions")

    Command.run('apache2 --version', True)
    Command.run('mysql --version', True)
    Command.run('composer --version', True)
    Command.run('symfony -V', True)

    print()
    heading("***")
    print()
    print("[OK] Thank you for your patience. The setup is now complete.")
    print()
except RuntimeError as e:
    print()
    print(e)
