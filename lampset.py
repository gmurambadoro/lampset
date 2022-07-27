#!/usr/bin/python3
import sys
from getpass import getpass
import subprocess

from command import Command

PHP_VERSIONS = [
    'php8.1',
    'php8.0',
    'php7.4', 
    'php7.2',     
]

OS_LSB_DESCRIPTION = "Debian GNU/Linux 11 (bullseye)"

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

    result = subprocess.run(['lsb_release', '-d'], stdout=subprocess.PIPE)
    description = result.stdout.decode(encoding='utf-8').strip().replace("Description:", "").strip()

    if OS_LSB_DESCRIPTION not in description:
        print(f"E: Unsupported Platform.\nExpecting `{OS_LSB_DESCRIPTION}` but found `{description}`")
        sys.exit(1)

    heading("System Upgrade")

    # upgrade the system first
    Command.run('sudo apt update', False)
    Command.run('sudo apt upgrade -y', False)

    heading("Registering PPAs")

    add_php_repo = """
    if [ "$(whoami)" != "root" ]; then
        SUDO=sudo
    fi

    ${SUDO} apt-get update \
    && ${SUDO} apt-get -y install apt-transport-https lsb-release ca-certificates curl \
    && ${SUDO} curl -sSLo /usr/share/keyrings/deb.sury.org-php.gpg https://packages.sury.org/php/apt.gpg \
    && ${SUDO} sh -c 'echo "deb [signed-by=/usr/share/keyrings/deb.sury.org-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/php.list' \
    && ${SUDO} apt-get update"""

    Command.run(add_php_repo, False)

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

    Command.run(add_apache2_repo, False)

    heading("Installing Apache and MySQL")

    Command.run('sudo apt install -y curl apache2 libapache2-mod-fcgid zip unzip', False)

    add_mysql_server = """
    sudo apt install -y wget \
        && wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb \
        && sudo apt install -y ./mysql-apt-config_0.8.22-1_all.deb \
        && rm mysql-apt-config_0.8.22-1_all.deb \
        && sudo apt update \
        && sudo apt install -y mysql-server  mysql-client \
        && sudo service mysql status 
    """

    Command.run(add_mysql_server, False)

    heading("Installing Multiple PHP Versions")

    # install multiple php versions
    for ver in PHP_VERSIONS:
        php_extensions = '{PHP_VER} {PHP_VER}-cli {PHP_VER}-common {PHP_VER}-curl {PHP_VER}-gd {PHP_VER}-mbstring ' \
                         '{PHP_VER}-zip {PHP_VER}-xml {PHP_VER}-sqlite3 {PHP_VER}-mysql {PHP_VER}-apcu ' \
                         '{PHP_VER}-fpm libapache2-mod-{PHP_VER} {PHP_VER}-intl {PHP_VER}-bcmath'.replace('{PHP_VER}', ver)

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
    Command.run("sudo apt update -y && sudo apt install symfony-cli -y", False)
    Command.run('symfony -V', False)

    print("LAMPSET VHOST-ADD")
    Command.run('rm -rf /tmp/lampset-vhost-add', True)
    Command.run('git clone https://github.com/gmurambadoro/lampset-vhost-add.git /tmp/lampset-vhost-add', False)
    Command.run('chmod +x /tmp/lampset-vhost-add/lampset-vhost-add.py', False)
    Command.run('sudo mv --force /tmp/lampset-vhost-add/lampset-vhost-add.py /usr/local/bin/vhost-add', False)
    Command.run('vhost-add --help', False)

    heading("Configuring MySQL")

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
    mysql> FLUSH PRIVILEGES;
    mysql> quit;
    """)
    try:
        Command.run("sudo mysql", False)
    except:
        print("")
        print("** It seems like you already have set the root password.")
        print("")
        # Command.run("mysql -uroot -p", False)

    res = input("""
Do you want to secure your MySQL installation by running `mysql_secure_installation`?

== NB: If already run, please select `N` to skip this part ==

Do yo want want to run `mysql_secure_installation` now (Y/n): """)

    if 'y' == str(res or '').strip().lower():
        Command.run('sudo mysql_secure_installation', False)

    heading('Node JS LTS')
    Command.run("curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -", False)
    Command.run("sudo apt-get install -y nodejs", False)
    Command.run("sudo npm install --location=global npm@latest", False)
    Command.run("sudo npm install --location=global maildev", False) # https://www.npmjs.com/package/maildev


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
    Command.run('node -v', True)
    Command.run('npm -v', True)

    print()
    heading("***")
    print()
    print("[OK] Thank you for your patience. The setup is now complete.")
    print()
except RuntimeError as e:
    print()
    print(e)
