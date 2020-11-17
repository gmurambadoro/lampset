# Linux Apache Setup (lapset)

**lapset** is a command line script written in Python that will allow you to setup a LAMP stack on a freshly installed Ubuntu-based virtual machine.

## Features

- Support for multiple PHP versions, namely **php5.6**, **php7.1**, **php7.2**, **php7.3** and **php7.4**.
- Latest version of **MySQL server** installed and properly configured.
- Support for **PHP-FPM** to allow simultaneous hosting of multiple sites that support different versions of PHP.
- Latest version of **composer** (version 2)
- Latest version of the **wkhtmltopdf** binary for automatic generation of HTML to PDF from the command-line.

## Requirements

- Debian-based Linux distribution e.g. [Ubuntu Server](https://ubuntu.com/download/server).
- Latest version of [git](https://git-scm.com/)

# Usage

- [Download](https://github.com/gmurambadoro/lapset/releases) the latest version of [*lapset*](https://github.com/gmurambadoro/lapset/releases) from our 
[releases](https://github.com/gmurambadoro/lapset/releases) page.
- Rename the downloaded file to *lapset* and make it executable.
- Run the executable file and boom, the setup is in progress.
    
    ```
    $ mv lapset-* lapset
    $ chmod +x lapset
    $ ./lapset
    ```

## Packaging

If you are going to build this package into a single binary, I recommend you use 
the [PyInstaller](https://pyinstaller.readthedocs.io/en/stable/). I found it to be simple and easy to use.

```
$ pyinstaller -onefile main.py
```