#!/usr/bin/python3
import subprocess
import sys
from getpass import getpass

import click

from xcommand import XCommand

PHP_VERSIONS = [
    'php8.1',
    'php8.0',
    'php7.4',
    'php7.2',
]

DEFAULT_PHP_VERSION = PHP_VERSIONS[0]

OS_RELEASES = ["Debian GNU/Linux 11 (bullseye)", "Raspbian GNU/Linux 11 (bullseye)"]


@click.command()
@click.option('--php', default=list(map(lambda x: str(x).replace("php", ""), PHP_VERSIONS)),
              help="Version(s) of PHP to install",
              show_default=True,
              type=click.STRING,
              multiple=True)
def lampset(php: list = None):
    if php is None:
        php = []

    php_versions = list(
        map(lambda x: f"php{x}".strip().lower() if "php" not in str(x).lower().strip() else str(x).strip().lower(), php)
    )

    php_not_supported = list(filter(lambda x: x not in PHP_VERSIONS, php_versions))

    if len(php_not_supported):
        click.echo(message=f"The following list of PHP versions is not supported: {php_not_supported}\n"
                           f"Allowed PHP values:  {PHP_VERSIONS}")
        return

    run_platform_check()

    run_system_upgrade()

    add_package_repositories()

    install_apache2_and_mariadb()

    install_php(php_versions=php_versions)

    fix_virtualbox_permissions()

    install_composer()

    if not is_raspberry_pi():
        install_symfony()

    install_vhost_utility()

    configure_mariadb()

    install_nodejs_and_packages()

    display_package_versions()

    print()
    section("***")
    print()
    print("[OK] Thank you for your patience. The setup is now complete.")
    print()


def is_raspberry_pi() -> bool:
    return "raspberry" in get_os_release().lower()


def get_os_release() -> str:
    result = subprocess.run(['lsb_release', '-d'], stdout=subprocess.PIPE)
    return result.stdout.decode(encoding='utf-8').strip().replace("Description:", "").strip()


def section(title: str) -> None:
    print()
    print(f"== {title} ==".upper())
    print()


def run_platform_check():
    # check if the platform is supported
    if sys.platform != 'linux':
        print(f'E: Your `{sys.platform}` platform is not supported. At the moment we support only `linux` which is '
              f'found in Ubuntu-based Linux distributions.')

        sys.exit(1)

    os_release = get_os_release()

    if get_os_release() not in OS_RELEASES:
        print(f"E: Unsupported Platform.\nExpecting any of {OS_RELEASES} but found \"{os_release}\"")
        sys.exit(1)


def run_system_upgrade():
    section("System Upgrade")

    # upgrade the system first
    XCommand.run('sudo apt update', False)
    XCommand.run('sudo apt upgrade -y', False)


def add_package_repositories():
    section("Registering PPAs")

    add_php_repo = """
        if [ "$(whoami)" != "root" ]; then
            SUDO=sudo
        fi
        ${SUDO} apt-get update \
        && ${SUDO} apt-get -y install apt-transport-https lsb-release ca-certificates curl \
        && ${SUDO} curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://packages.sury.org/php/apt.gpg \
        && ${SUDO} sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' \
        && ${SUDO} apt-get update"""

    XCommand.run(add_php_repo, False)

    add_apache2_repo = """
        if [ "$(whoami)" != "root" ]; then
            SUDO=sudo
        fi
        ${SUDO} apt-get update \
        && ${SUDO} apt-get -y install apt-transport-https lsb-release ca-certificates curl \
        && ${SUDO} curl -sSLo /usr/share/keyrings/deb.sury.org-apache2.gpg https://packages.sury.org/apache2/apt.gpg \
        && ${SUDO} sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-apache2.gpg] https://packages.sury.org/apache2/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/apache2.list' \
        && ${SUDO} apt-get update

        """

    XCommand.run(add_apache2_repo, False)


def install_apache2_and_mariadb():
    section("Installing Apache and MySQL")

    XCommand.run('sudo apt install -y curl apache2 libapache2-mod-fcgid zip unzip mariadb-server', False)


def install_php(php_versions: list):
    section("Installing Multiple PHP Versions")

    # install multiple php versions
    for ver in php_versions:
        php_extensions = '{PHP_VER} {PHP_VER}-cli {PHP_VER}-common {PHP_VER}-curl {PHP_VER}-gd {PHP_VER}-mbstring ' \
                         '{PHP_VER}-zip {PHP_VER}-xml {PHP_VER}-sqlite3 {PHP_VER}-mysql {PHP_VER}-apcu ' \
                         '{PHP_VER}-fpm libapache2-mod-{PHP_VER} {PHP_VER}-intl {PHP_VER}-bcmath'.replace('{PHP_VER}',
                                                                                                          ver)

        XCommand.run('sudo apt install -y ' + php_extensions, False)

    # set the default php version
    XCommand.run('sudo update-alternatives --config php', False)

    section("Configuring Default PHP Version for Apache")

    # set default apache php to latest php version
    XCommand.run('sudo a2enmod ' + DEFAULT_PHP_VERSION, True)
    XCommand.run('sudo systemctl restart apache2', False)

    section('PHP FPM')

    for ver in php_versions:
        XCommand.run('sudo systemctl start %s-fpm' % ver, False)

    XCommand.run('sudo a2enmod actions fcgid alias proxy_fcgi rewrite', False)
    XCommand.run('sudo systemctl restart apache2', False)


def fix_virtualbox_permissions():
    section("Setting Up User Permissions")

    # add the current user to the www-data group
    XCommand.run('sudo usermod -a -G www-data $USER', False)
    XCommand.run('sudo usermod -a -G vboxsf $USER', True)

    # allow apache2 to have read/write access to virtualbox shared folders
    XCommand.run('sudo usermod -a -G vboxsf www-data', True)

    print("[OK] Permissions were setup successfully.")


def install_composer():
    section("COMPOSER")

    # @see https://getcomposer.org/doc/faqs/how-to-install-composer-programmatically.md
    XCommand.run('wget https://raw.githubusercontent.com/composer/getcomposer.org'
                 '/76a7060ccb93902cd7576b67264ad91c8a2700e2/web/installer -O - -q | php -- --quiet', False)
    XCommand.run('chmod +x composer.phar', False)
    XCommand.run('sudo mv composer.phar /usr/local/bin/composer', False)
    XCommand.run('composer --version', False)


def install_symfony():
    section('SYMFONY')

    XCommand.run(
        "echo 'deb [trusted=yes] https://repo.symfony.com/apt/ /' | sudo tee /etc/apt/sources.list.d/symfony-cli.list",
        False)
    XCommand.run("sudo apt update -y && sudo apt install symfony-cli -y", False)
    XCommand.run('symfony -V', False)


def install_vhost_utility():
    print("LAMPSET VHOST-ADD")
    XCommand.run('rm -rf /tmp/lampset-vhost-add', True)
    XCommand.run('git clone https://github.com/gmurambadoro/lampset-vhost-add.git /tmp/lampset-vhost-add', False)
    XCommand.run('chmod +x /tmp/lampset-vhost-add/lampset-vhost-add.py', False)
    XCommand.run('sudo mv --force /tmp/lampset-vhost-add/lampset-vhost-add.py /usr/local/bin/vhost-add', False)
    XCommand.run('vhost-add --help', False)


def configure_mariadb():
    section("Configuring MySQL")

    password = "password"
    confirm_password = "confirm_password"

    while password != confirm_password:
        password = str(getpass("Enter a password for the root user: ")).strip()
        confirm_password = str(getpass("Repeat the root password: ")).strip()

        if password != confirm_password:
            print("Passwords don't match!")

    print("")
    print("Run the following commands in your terminal.")
    print(f"""
        mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '{password}';
        mysql> GRANT ALL ON *.* TO 'admin'@'localhost' IDENTIFIED BY '{password}' WITH GRANT OPTION;
        mysql> FLUSH PRIVILEGES;
        mysql> quit;
        """)
    try:
        XCommand.run("sudo mysql", False)
    except RuntimeError:
        print("")
        print("** It seems like you already have set the root password.")
        print("")

    res = input("""
    Do you want to secure your MySQL installation by running `mysql_secure_installation`?

    == NB: If already run, please select `N` to skip this part ==

    Do yo want want to run `mysql_secure_installation` now (Y/n): """)

    if 'y' == str(res or '').strip().lower():
        XCommand.run('sudo mysql_secure_installation', False)


def install_nodejs_and_packages():
    section('Node JS LTS')
    XCommand.run("curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -", False)
    XCommand.run("sudo apt-get install -y nodejs", False)
    XCommand.run("sudo npm install --location=global npm@latest", False)
    XCommand.run("sudo npm install --location=global maildev", False)  # https://www.npmjs.com/package/maildev


def display_package_versions():
    section("PHP Versions")

    for ver in PHP_VERSIONS:
        XCommand.run('%s --version' % ver, False)

    section("Default PHP Version")

    XCommand.run('php --version', True)

    section("Software Versions")

    XCommand.run('apache2 --version', True)
    XCommand.run('mysql --version', True)
    XCommand.run('composer --version', True)

    if not is_raspberry_pi():
        XCommand.run('symfony -V', True)

    XCommand.run('node -v', True)
    XCommand.run('npm -v', True)


if __name__ == "__main__":
    lampset()

