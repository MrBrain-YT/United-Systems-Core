<p align="center">
  <img src="USC.png" alt="Sublime's custom image"/>
</p>

# United Systems Core

United Systems Core is a system designed to simplify the process of creating, managing and integrating Python packages for the Flask web framework, designed for managing IoT devices and creating various web services.

## Commands for controll
- `install`: Install a package from USCServer or GitHub.

    ```bash
    usc install "package_name"
    ```
    or
    ```bash
    usc install "https://github.com/autor/repo.git"
    ```

- `import`: Import a package from `tar.gz` file

    ```bash
    usc import "path/to/you.tar.gz"
    ```
    
- `remove`: Remove a package.

    ```bash
    usc remove "package_name"
- `refresh`: Refresh package data and install packages dependencies.

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
- `static`: Open the static folder.

    ```bash
    usc static
- `server`: Set data for the server from which packages are downloaded.
        
    ```bash
    usc server "host:port"
- `config`: Set data for the server on which the packages are launched.
        
    ```bash
    usc config "host:port"
- `-h`: Get a help message.
- `-v`: Get USC version.



## Install
- GIT
    ```bash
    git clone https://github.com/MrBrain-YT/United-Systems-Core.git
    ```

- Docker
    ```bash
    docker build -t usc .
    ```
    <p align="center">and</p>
    
    ```bash
    docker run -t -d usc
    ```



## How to create package
To create a package, you need to follow certain rules:

- You need to create a package template using a command
    

    ```bash
    usc create "package_name"
    ```

- Afterward, open the package in any available supported IDE (```VS Code```, ```Vim```) using the command
    ```bash
    usc code "package_name"
    ```
    
    When you create a package, you will automatically create a python file with an example of the package home page

- After you have created a package template and started modifying it, you should follow certain rules:
    
    - The URL path to your package should ideally be written according to this principle ```/package_name/...``` to avoid conflicts between different packages.

        ```python
        @app.route('/package_name/...', methods = ['GET'])
        ```
    - To add an HTML page, you need to open the "templates" directory using the command
        ```bash
        usc templates
        ```
        
        There, you need to find the directory of your package and place your HTML files in it. To use your HTML file in the render_template function, you need to specify the path as ```/package_name/test.html```.
        ```python
        return render_template("test/test.html")
        ```

- To add JS and CSS scripts, you can use the "static" folder in your package directory.
To open the "static" directory, use the command:
    ```bash
    usc static
    ```
    
    
    Example usage in HTML:
    ```html
    <link rel="stylesheet" type="text/css" href="/static/```package_name/index.css">
    ```

- Any python files will automatically check during startup for the presence of the ```main``` function and whether it accepts the ```app``` argument. If an error is detected in your file, it will not be launched automatically and information about it will be displayed in the console. If your file does not have a main function, then it is considered auxiliary. The function launched through the ```run``` command must meet certain requirements:

    - It should accept the argument "app"

        ```python
        def main(app:Flask):
        ```
    - It should run a function whose name is main

- To import custom modules, you should use the following structure:
    ```python
    import packages.package_name.you_module
    ```

- In each package, there is a `requirements.txt` file that contains the necessary libraries for the package to function. These libraries are automatically downloaded when the package is installed or when the package list is refreshed using the `refresh` command. When a package is removed using the `remove` command, the associated libraries are also removed. If two packages use the same library, it's important to update the package list after removing a package to ensure that the list reflects the correct dependencies.


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


