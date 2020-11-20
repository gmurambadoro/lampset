# Linux, Apache, MySQL & PHP (LAMP) Setup

**lampset** is a command line script written in Python that will allow you to setup a LAMP stack on a freshly installed Ubuntu-based virtual machine.

## Features

- Support for multiple PHP versions, namely **php5.6**, **php7.1**, **php7.2**, **php7.3** and **php7.4**.
- Latest version of **MySQL server** installed and properly configured.
- Support for **PHP-FPM** to allow simultaneous hosting of multiple sites that support different versions of PHP.
- Latest version of **composer** (version 2)
- Latest version of the **wkhtmltopdf** binary for automatic generation of HTML to PDF from the command-line.

## Requirements

- Debian-based Linux distribution e.g. [Ubuntu Server](https://ubuntu.com/download/server).
- [Git](https://git-scm.com/) - latest version.
- **Python 3.8** or greater

# Usage

```
$ git clone https://github.com/gmurambadoro/lampset.git
$ cd lampset
$ python3 lampset.py
```
