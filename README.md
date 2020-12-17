# Linux, Apache, PHP & MySQL Setup (lampset)

**lampset** is a LAMP stack provisioning script specifically targeting Ubuntu-based distributions, for example **Linux Mint**, **Ubuntu Server** and **Ubuntu Server on VirtualBox**.

## Features

- (L)inux: Ubuntu-based distribution e.g. Linux Mint, Ubuntu Server and Ubuntu Server on VirtualBox
- (A)pache2 - latest version
- (M)ySQL version 5.7
- (P)HP versions **php5.6**, **php7** and **php8.0**.
	- PHP-FPM allows you to run multiple sites running under different PHP versions at the same time.

For general-purpose web development support, the following packages are also installed:

- [Composer version 2](https://getcomposer.org/)
- [Symfony CLI](https://symfony.com/download)

## Brief History

As a web and back end developer I always had a need for an LAMP stack environment that I can use for developing different web-based applications. The major requirement was that the environment needed to support multiple versions of PHP at the same time - a problem solved by [PHP FPM](https://www.php.net/manual/en/install.fpm.php).

The **lampset** binary is the bringing together of all of the knowledge acquired from the Internet on how to bring this environment up and running in no time, especially after a fresh installation of an operating system.

## Supported Platforms

- Ubuntu-based Linux operating systems e.g. [Linux Mint](https://linuxmint.com) and [Ubuntu Server](https://ubuntu.com/download/server). 
- All other operating systems (e.g. Mac, Windows) are supported via [VirtualBox](https://virtualbox.org). The only requirement is that the guest operating system needs to be [Ubuntu Server](https://ubuntu.com/download/server).

## How it works

**lampset** is an encapsulation of various `bash` commands and concepts that are applied when setting up a LAMP stack on Ubuntu Server or its variants.

The following are more or less the steps that are taken during the provisioning process. Some of the steps require human intervention, so you need to stick around for the duration of the setup.

- Perform a system upgrade to ensure that every package is up to date.
- Register *ppa:ondrej/php* and *ppa:ondrej/apache2* Personal Package Archives (PPAs) that will act as official repositories for PHP and Apache2 respectively.
- Install Apache, MySQL and support modules.
- Install PHP versions **php5.6**, **php7.1**, **php7.2**, **php7.3**, **php7.4** and **php8.0**.
- For each PHP version install various extension modules that are commonly used in a web development environment but not in the core package. Additionally install the respective PHP-FPM module as well.
- Configure the default PHP version to be used by `apache2`.
- Run `mysql_secure_installation` to set up root account details and default configuration of MySQL server.
- Fix `mysql` configuration so that clients like WorkBench can connect to it without running into `Access Denied/Permission" issues.
- Install some opinionated packages that I always need namely [Composer](https://getcomposer.org) and [Symfony CLI](https://symfony.com/download).

## Installation

To setup the LAMP server simply clone this repository and execute the `lampset.py` file. In this example I have cloned into the `/tmp/` directory because this script should only be run once. The system will delete the contents of `/tmp/` on next boot. 

```
$ cd /tmp/
$ git clone https://github.com/gmurambadoro/lampset.git
$ cd lampset/
$ python3 lampset.py
```

## Post Installation

After the setup is complete, I recommend you install my other package called [`lampset-vhost-add`](https://github.com/gmurambadoro/lampset-vhost-add). This will allow you to easily add virtual hosts for your various projects and at the same time specify the PHP versions these need to run on.

```
$ cd ~
$ git clone https://github.com/gmurambadoro/lampset-vhost-add.git
$ cd lampset-vhost-add/
$ chmod +x lampset-vhost-add
$ sudo mv lampset-vhost-add /usr/local/bin/vhost-add
$ vhost-add --help
$ vhost-add --interactive
```
