import sys
from getpass import getpass

from command import Command


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
        Command.run(f'sudo add-apt-repository {ppa}', False)

    Command.run('sudo apt update -y', False)

    heading("Installing Apache and MySQL")

    Command.run('sudo apt install -y curl apache2 libapache2-mod-fcgid', False)
    Command.run('sudo apt install -y mysql-server mysql-client', False)

    heading("Installing Multiple PHP Versions")

    # install multiple php versions
    for ver in ['5.6', '7.1', '7.2', '7.3', '7.4']:
        php_extensions = '{PHP_VER} {PHP_VER}-cli {PHP_VER}-common {PHP_VER}-curl {PHP_VER}-gd {PHP_VER}-mbstring ' \
                         '{PHP_VER}-zip {PHP_VER}-xml {PHP_VER}-sqlite3 {PHP_VER}-mysql {PHP_VER}-apcu ' \
                         '{PHP_VER}-fpm libapache2-mod-{PHP_VER}'.replace('{PHP_VER}', 'php' + ver)

        Command.run('sudo apt install -y ' + php_extensions, False)

    # set the default php version
    Command.run('sudo update-alternatives --config php', False)

    heading("Configuring Default PHP Version for Apache")

    # set default apache php to 7.4
    Command.run('sudo a2dismod php5.6', False)
    Command.run('sudo systemctl restart apache2', False)
    Command.run('sudo a2enmod php7.4', False)
    Command.run('sudo systemctl restart apache2', False)

    heading("Setting Up User Permissions")

    # add the current user to the www-data group
    Command.run('sudo usermod -a -G www-data $USER', False)
    Command.run('sudo usermod -a -G vboxsf $USER', False)

    # allow apache2 to have read/write access to virtualbox shared folders
    Command.run('sudo usermod -a -G vboxsf www-data', False)

    heading("WKHTMLTOPDF")

    # install wkhtmltopdf
    Command.run('sudo apt install -y wkhtmltopdf', False)

    heading("COMPOSER")

    Command.run('bash composer-install.sh', False)
    Command.run('sudo chmod +x composer.phar', False)
    Command.run('sudo mv composer.phar /usr/local/bin/composer', False)
    Command.run('composer --version', False)

    heading("Configuring MySQL")

    res = input('Do you want to secure your MySQL installation by running `mysql_secure_installation`? (Y/n): ')

    if 'y' == str(res or '').strip().lower():
        Command.run('sudo mysql_secure_installation', False)

    msg = """
If you frequently connect to MySQL via third party clients like Workbench and phpMyAdmin you might run into
`MySQL Access Denied` issues.

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

    print()
    print("[OK] Thank you for your patience. The setup is now complete.")
except RuntimeError as e:
    print()
    print(e)
