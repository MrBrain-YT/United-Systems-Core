# PackageManager class for usc methods

import os
import configparser
import shutil
import requests
import os
import re
import tarfile
import stat
from subprocess import call, Popen
import importlib
import platform

import git
from pyfiglet import Figlet
from tqdm import tqdm
from flask import Flask
from terminaltables import AsciiTable

from __list_work import ListWorker

# Class for progress bar when downloading from GitHub
class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print('\r' + message, end='', flush=True)

    def line_dropped(self, line):
        print(line)

    def sideband_progress(self, data):
        print('\r' + data, end='', flush=True)

# Main methods class 
class PackageManager():
    
    def __init__(self) -> None:
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.list = ListWorker()
    
    # install package
    def install(self, name:str) -> None:
        name = name.lower()
        if not self.list.check_exits(name):
            # Get download server info from run.ini
            server_config = configparser.ConfigParser()
            server_config.read(f"{self.current_directory}/run.ini") 
            host = server_config["DOWNLOAD"].get("host")
            port = server_config["DOWNLOAD"].get("port")
            # Get package
            data = {
                "package_name" : name
                }
            response = requests.post(url=f"http://{host}:{port}/package", data=data)
            # Checking valid server data
            if response.status_code == 200:
                
                # Get tar-gz file from server
                filename = f'{self.current_directory}/temp/{name}.tar.gz'
                total_size = int(response.headers.get('content-length', 0))
                with open(filename, 'wb') as f, tqdm(
                    total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
                    desc=f"Downloading {name} ", initial=0, miniters=1) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = f.write(data)
                        bar.update(size)
                        
                # extracting file
                dir_path = f"{self.current_directory}/packages"
                file = tarfile.open(f"{self.current_directory}/temp/{name}.tar.gz") 
                file.extractall(dir_path) 
                file.close()
                os.remove(f'{self.current_directory}/temp/{name}.tar.gz')
                
                # move template folder
                package_templates_dir = f"{self.current_directory}/templates/{name}"
                shutil.copytree(f"{dir_path}/{name}/templates", package_templates_dir)
                shutil.rmtree(f"{dir_path}/{name}/templates")
                
                # Get properties from package.ini
                package_config = configparser.ConfigParser()
                package_config.read(f"{dir_path}/{name}/package.ini")
                        
                self.list.add_package_to_list(package_config=package_config)
            else:
                print("Package not found in server")
        else:
            print("Package alredy exist")
    
    @staticmethod
    def on_rm_error(func, path, exc_info) -> None:
        #from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
    
    # install package from git 
    def install_git(self, url:str) -> None:
        dir_path = f'{self.current_directory}/temp/git'
        code = requests.get(url).status_code
        if code == 200:
            # Clone repo from using URL
            git.Repo.clone_from(url, dir_path, progress=Progress())
            
            # Check package
            package_dir_path = f"{dir_path}/{[folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")][1]}"
            if os.path.exists(f"{package_dir_path}/package.ini"):
                package_config = configparser.ConfigParser()
                package_config.read(f"{package_dir_path}/package.ini")
                package_name = package_config["INFO"].get("name")
                package_version = package_config["INFO"].get("version")
                if package_name and package_version != None:
                    pattern = r"[!@#$%^&*(),?\":{}|<>]"
                    if re.search(pattern, package_name) or re.search(pattern, package_version):
                        error = True
                    else:
                        if not self.list.check_exits(package_name):
                            # add package to list
                            self.list.add_package_to_list(package_config=package_config)
                            # move dir to packages
                            package_template_folder = f"{self.current_directory}/templates/{package_name}"
                            shutil.copytree(f"{package_dir_path}/templates", package_template_folder)
                            shutil.rmtree(f"{package_dir_path}/templates")
                            shutil.move(package_dir_path, f"{self.current_directory}/packages")
                        else:
                            print("\nPackage alredy exits")          
                else:
                    print("\nInvalid package")
            else:
                print("\nPackage does not contain package.ini")
        else:
            print("url not valid")
            return None

        # delete .git folder
        for i in os.listdir(dir_path):
            if i.endswith('git'):
                tmp = os.path.join(dir_path, i)
                # We want to unhide the .git folder before unlinking it.
                while True:
                    call(['attrib', '-H', tmp])
                    break
                shutil.rmtree(tmp, onerror=self.on_rm_error)
        # delete git folder
        shutil.rmtree(dir_path)

    
    # remove package 
    def remove(self, names:list[str]) -> None:
        for name in names:
            # If name == "*" then remove all packages
            if name == "*":
                # Geting all packages from packages directory
                dir_path = f"{self.current_directory}/packages"
                packages = [folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")]
                # Removing packages
                for package in packages:
                    self.list.remove_package_from_list(name=package)
                    shutil.rmtree(f"{self.current_directory}/packages/{package}")
                    shutil.rmtree(f"{self.current_directory}/templates/{package}")
                    print(f"Package {package} removed")
                break
            
            # remove pacage if package in packages.ini
            elif self.list.check_exits(name=name):
                self.list.remove_package_from_list(name=name)
                shutil.rmtree(f"{self.current_directory}/packages/{name}")
                shutil.rmtree(f"{self.current_directory}/templates/{name}")
                print(f"Package {name} removed")
            
            # package not found
            else:
                print("Package not found")
    
    # create package
    def create(self, names:list[str]) -> None:
        for name in names:
            package_version = "0.0.1"
            # Check on not exist package in packages.ini file
            if not self.list.check_exits(name):
                
                # Creating package folder
                os.makedirs(f"{self.current_directory}/packages/{name}")
                os.makedirs(f"{self.current_directory}/templates/{name}")
                
                # creating new package.ini file
                with open(f"{self.current_directory}/packages/{name}/package.ini", "w") as ini_file:
                    ini_file.write(f"[INFO]")
                    ini_file.write(f"\nname = {name}")
                    ini_file.write(f"\nversion = {package_version}")
                
                # Add package to packages.ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{name}/package.ini")
                self.list.add_package_to_list(package_config=package_config)
            else:
                print("Package alredy exits")

    # get packages list
    def get_list(self) -> str:
        # Open packages.ini file
        config = configparser.ConfigParser()
        config.read(f"{self.current_directory}/packages/packages.ini")
        
        # Creating table data
        table_data = [['Name', "Version"]]
        for pack in config.sections():
            table_data.append([
                config[pack].get("name"),
                config[pack].get("version")
            ])
        # Creating table
        table = AsciiTable(table_data)
        
        return table.table
    
    # run server
    def run(self, package:str=None) -> None:
        app = Flask("United Systems Core", template_folder=f'{self.current_directory}/templates')
        
        # Get packages for running
        packages_folder = f"{self.current_directory}/packages"
        packages = [
                    package for package in os.listdir(packages_folder) 
                    if os.path.isdir(f"{packages_folder}/{package}")
                    ] if package == None else package.split(",")
        
        # Importing packages modules
        for package in packages:
            package_folder = f"{self.current_directory}/packages/{package}"
            package_files = [package for package in os.listdir(package_folder) if ".py" in package]
            for package_file in package_files:
                package_module = importlib.util.spec_from_file_location(package_file.replace(".py", ""), f"{package_folder}/{package_file}")
                package = importlib.util.module_from_spec(package_module)
                package_module.loader.exec_module(package)
                module_function = [func for func in dir(package) if not func.startswith('__')][-1]
                getattr(package, module_function)(app)
                
        # run server using data from run.ini
        server_config = configparser.ConfigParser()
        server_config.read(f"{self.current_directory}/run.ini") 
        host = server_config["SERVER"].get("host")
        port = server_config["SERVER"].get("port")
        app.run(host=host, port=port)

    # export package
    def export(self, names:list[str]) -> None:
        # export package to current opened directory
        for name in names:
            if self.list.check_exits(name):
                # Get package folders
                pack_dir = f"{self.current_directory}/packages/{name}"
                pack_templates_dir = f"{self.current_directory}/templates/{name}"
                try:
                    # Creating temp temoplates file in package folder
                    shutil.copytree(pack_templates_dir, f"{pack_dir}/templates")
                    
                    # creating tar.gz file
                    with tarfile.open(f"{os.getcwd()}/{name}.tar.gz", "w:gz") as tar:
                        tar.add(pack_dir, arcname=os.path.basename(pack_dir))
                        
                    # Removing temp temoplates file in package folder
                    shutil.rmtree(f"{pack_dir}/templates")
                    print("Package exported")
                    
                except Exception as e:
                    print(f"Error:\n{e}")
            else:
                "Package not found"
            
    # open package in IDE
    def code(self, name:str, ide:str=None, no_package:bool=False) -> None:
        if self.list.check_exits(name=name) or no_package:
            pack_dir = f"{self.current_directory}/packages/{name}" \
                if no_package == False else f"{self.current_directory}/packages/"
                
            # Automatic get IDE
            if ide is None:
                # vscode
                if shutil.which('code') != None:
                    Popen([shutil.which('code'), pack_dir], shell=False)
                    print("Opened with VS Code")
                # vim
                elif shutil.which('vim') != None:
                    Popen([shutil.which('vim'), pack_dir], shell=False)
                    print("Opened with Vim")
                # no ide
                else:
                    print("IDE not found")
                
            else:
                # Manually getting the IDE
                ide = ide.replace("--", "")
                # vscode
                if ide == "vscode":
                    if shutil.which('code') != None:
                        Popen([shutil.which('code'), pack_dir], shell=False)
                        print("Opened with VS Code")
                    else:
                        "VS Code not found"
                # vim
                elif ide == "vim":
                    if shutil.which('vim') != None:
                        Popen([shutil.which('vim'), pack_dir], shell=False)
                        print("Opened with Vim")
                    else:
                        "Vim not found"
                # no ide
                else:
                    print("IDE not selected")
        else:
            print("Package not found")
            
    def templates(self):
        # Open templates folder
        path = f"{self.current_directory}/templates"
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            Popen(["open", path])
        else:
            Popen(["xdg-open", path])
    
    # set config file for local server and packages server
    def set_server_config(self, server_info:str, is_my_server:bool) -> None:
        config = configparser.ConfigParser()
        config.read(f'{self.current_directory}/run.ini')
        # Checking which parameter needs to be changed
        if is_my_server:
            host, port = server_info.split(":")
            config['SERVER'] = {'host': host,
                                'port': port}
            with open(f'{self.current_directory}/run.ini', 'w') as configfile:
                config.write(configfile)
        else:
            host, port = server_info.split(":")
            config['DOWNLOAD'] = {'host': host,
                                'port': port}
            with open(f'{self.current_directory}/run.ini', 'w') as configfile:
                config.write(configfile)
          
    # refresh packages folder
    def refresh(self) -> None:
        # clear packages list
        with open(f"{self.current_directory}/packages/packages.ini", 'w') as configfile:
            configfile.write("")
        # get files from directory
        files = [
            file for file in os.listdir(f"{self.current_directory}/packages") 
            if os.path.isdir(f"{self.current_directory}/packages/{file}")
            ]
        
        for file in files:
            # Checking exist package.ini file
            if os.path.exists(f"{self.current_directory}/packages/{file}/package.ini"):
                
                # Open packages ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{file}/package.ini")
                
                # checking templates folder
                if not os.path.exists(f"{self.current_directory}/templates/{file}"):
                    os.mkdir(f"{self.current_directory}/templates/{file}")
                    
                # Add package to list 
                self.list.add_package_to_list(package_config=package_config)
            else:
                # Create package.ini file
                with open(f"{self.current_directory}/packages/{file}/package.ini", "w") as file_version:
                    file_version.write(f"[INFO]")
                    file_version.write(f"\nname = {file}")
                    file_version.write("\nversion = 0.0.1")
                
                # read created package.ini fale and add package to packages.ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{file}/package.ini")
                os.mkdir(f"{self.current_directory}/templates/{file}")
                self.list.add_package_to_list(package_config=package_config)
              
    def update_algorithm(self):
        # Cloning repo
        dir_path = f"{self.current_directory}/temp"
        os.mkdir(f"{dir_path}/update")
        url = "https://github.com/MrBrain-YT/United-Systems-Core.git"
        git.Repo.clone_from(url, f"{dir_path}/update", progress=Progress())
        
        # removing old files
        remove_files = [file for file in os.listdir(self.current_directory) if ".py" in file]
        remove_files.append("version")
        for file in remove_files:
            os.remove(os.path.join(self.current_directory, file))
            
        # Restor new py files add version file
        new_main_files = [file for file in os.listdir(f"{dir_path}/update/usc") if ".py" in file]
        new_main_files.append("version")
        for file in new_main_files:
            shutil.copy2(os.path.join(f"{dir_path}/update/usc", file), self.current_directory)
            
        # Restor packages file 
        new_packages_files = [file for file in os.listdir(f"{dir_path}/update/usc/packages") if "packages.ini" != file]
        for file in new_packages_files:
            full_path = os.path.join(f"{dir_path}/update/usc/packages", file)
            if os.path.isdir(full_path):
                shutil.copytree(full_path, f"{self.current_directory}/packages")
            else:
                shutil.copy2(full_path, f"{self.current_directory}/packages")
            
        # Restor templates file 
        new_templates_files = [file for file in os.listdir(f"{dir_path}/update/usc/templates")]
        for file in new_templates_files:
            full_path = os.path.join(f"{dir_path}/update/usc/templates", file)
            if os.path.isdir(full_path):
                shutil.copytree(full_path, f"{self.current_directory}/templates")
            else:
                shutil.copy2(full_path, f"{self.current_directory}/templates")
                
        # delete .git folder
        for i in os.listdir(f"{dir_path}/update"):
            if i.endswith('git'):
                tmp = os.path.join(f"{dir_path}/update", i)
                # We want to unhide the .git folder before unlinking it.
                while True:
                    call(['attrib', '-H', tmp])
                    break
                shutil.rmtree(tmp, onerror=self.on_rm_error)
        # delete update folder
        shutil.rmtree(f"{dir_path}/update")
                
                
    def update(self):
        version = requests.get("https://raw.githubusercontent.com/MrBrain-YT/United-Systems-Core/main/USC/version")
        if version.status_code == 200:
            with open(f'{os.path.dirname(os.path.abspath(__file__))}/version', "r") as ver:
                local_version = ver.read()
                
            local_version = local_version.split(".")
            version = version.text.split(".")
            if (int(version[0]) > int(local_version[0])):
                self.update_algorithm()    
            else:
                if int(version[1]) > int(local_version[1]):
                    self.update_algorithm()
                else:
                    if int(version[2]) > int(local_version[2]):
                        self.update_algorithm()
                    else:
                        print("Latest version already installed")
        else:
            print("Url not valid")
            
    @staticmethod
    def help_message() -> dict:
        message_data = {
            "install": "Install package from USCServer and GitHub",
            "remove": "Remove package",
            "refresh": "Refrash packages data",
            "list": "Get list installed packages",
            "update": "Upadate United Systems Core",
            "run": "Start the server with all packages or only with selected ones",
            "export": "Export package to curent opened in terminal folder",
            "code": "Open packages or package in IDE (vs code, vim)",
            "templates": "Open templates folder",
            "server": "Set data for the server from which packages are downloaded",
            "config": "Set data for the server on which the packages are launched",
            "-h": "Get help message",
            "-v": "Get USC version",
        }
        return message_data
    
    def core_version():
        with open(f'{os.path.dirname(os.path.abspath(__file__))}/version', "r") as ver:
            version = ver.read()
        preview_text = Figlet(font='larry3d')
        print(preview_text.renderText('------'))
        print(preview_text.renderText(f'V-{version}'))
        print(preview_text.renderText('------'))