<p align="center">
  <img src="USC.png" alt="Sublime's custom image"/>
</p>

# United Systems Core

United Systems Core - system designed to simplify the process of creating, managing, and integrating Python packages for the Flask web framework, intended for managing IoT devices.

## Commands for controll
- `install`: Install a package from USCServer or GitHub.

    ```bash
    usc install "package_name"
    ```
    or
    ```bash
    usc install "https://github.com/autor/repo.git"
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


## How to create package
To create a package, you need to follow certain rules:

- You need to create a package template. This can be done in several ways.
    
    - Creating using a command

        ```bash
        usc create "package_name"
        ```
    - Creating using the refresh command. More precisely, you can ```create an empty folder``` in the package directory, and then ```use the refresh command```, which will turn the empty folder into a directory for a new package and add the new package to the list.
- Afterward, open the package in any available supported IDE (```VS Code```, ```Vim```) using the command
    ```bash
    usc code "package_name"
    ```

- After you have created a package template and started modifying it, you should follow certain rules:
    
    - The URL path to your package should ideally be written according to this principle ```/package_name/...``` to avoid conflicts between different packages.

        ```bash
        @app.route('/package_name/...', methods = ['GET'])
        ```
    - To add an HTML page, you need to open the "templates" directory using the command
        ```bash
        usc templates
        ```
        
        There, you need to find the directory of your package and place your HTML files in it. To use your HTML file in the render_template function, you need to specify the path as ```/package_name/test.html```.
        ```bash
        return render_template("test/test.html")
        ```


## Example package for USC
You can find an example package for USC at the following link: https://github.com/MrBrain-YT/test-usc-package

To download the package, use the command:
    
    usc install https://github.com/MrBrain-YT/test-usc-package.git


## Make a contribution
To contribute to this project, you can:

- Create packages.

- Write additions and fixes for USC and USCServer.

- connect to discord - https://discord.gg/zAmJG5apZK


## Additional information
USCServer - https://github.com/MrBrain-YT/USCServer

test-usc-package - https://github.com/MrBrain-YT/test-usc-package


