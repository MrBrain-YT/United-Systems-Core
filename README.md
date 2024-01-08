# United Systems Core

United Systems Core - system designed to simplify the process of creating, managing, and integrating Python packages for the Flask web framework, intended for managing IoT devices.

# Commands for controll
- `install`: Install a package from USCServer or GitHub.

    ```bash
    usc install "package_name"
    ```
    or
    ```bash
    usc install https://github.com/MrBrain-YT/test-usc-package.git
    ```
    
- `remove`: Remove a package.

    ```bash
    usc remove "package_name"
- `refresh`: Refresh package data.

    ```bash
    usc refresh
- `list`: Get a list of installed packages.

    ```bash
    usc list
- `update`: Update United Systems Core.

    ```bash
    usc update
- `run`: Start the server with all packages or only with selected ones.

    ```bash
    usc run
    ```
    or
    ```bash
    usc run "package_name, ..."
- `export`: Export a package to the current folder opened in the terminal.

    ```bash
    usc export "package_name, ..."
- `code`: Open packages or a package in an IDE (VS Code, Vim).
    ```bash
    usc code
    ```
    or
    ```bash
    usc code "package_name, ..."
- `templates`: Open the templates folder.

    ```bash
    usc templates
- `server`: Set data for the server from which packages are downloaded.
        
    ```bash
    usc server "host:port"
- `config`: Set data for the server on which the packages are launched.
        
    ```bash
    usc config "host:port"
- `-h`: Get a help message.
- `-v`: Get USC version.



## Install

    git clone https://github.com/MrBrain-YT/United-Systems-Core.git


## Example package for USC
You can find an example package for USC at the following link: https://github.com/MrBrain-YT/test-usc-package

To download the package, use the command:
    
    usc install https://github.com/MrBrain-YT/test-usc-package.git



