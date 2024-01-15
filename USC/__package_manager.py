# PackageManager class for usc methods

import os
import configparser
import shutil
import requests
import os
import re
import tarfile
import stat
import sys
from subprocess import call, Popen, check_call
import importlib
import platform

import git
from colorama import Fore
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
            name = name.lower()
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
                
                check_call([sys.executable, "-m", "pip", "install", "-r", f"{self.current_directory}/packages/{name}/requirements.txt"], shell=False)
                
                # move template folder
                package_templates_dir = f"{self.current_directory}/templates/{name}"
                shutil.copytree(f"{dir_path}/{name}/templates", package_templates_dir)
                shutil.rmtree(f"{dir_path}/{name}/templates")
                
                # move static folder
                package_static_dir = f"{self.current_directory}/static/{name}"
                shutil.copytree(f"{dir_path}/{name}/static", package_static_dir)
                shutil.rmtree(f"{dir_path}/{name}/static")
                
                # Get properties from package.ini
                package_config = configparser.ConfigParser()
                package_config.read(f"{dir_path}/{name}/package.ini")
                        
                self.list.add_package_to_list(package_config=package_config)
                print(Fore.GREEN + f"Package {name} installed")
            else:
                print(Fore.RED + "Package not found in server")
        else:
            print(Fore.RED + "Package alredy exist")
            
    # import package
    def import_package(self, paths:list) -> None:
        for path in paths:
            if os.path.exists(path):
                # extracting file
                dir_path = f"{self.current_directory}/temp"
                start_package_dir_path = [folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")]
                file = tarfile.open(path) 
                file.extractall(dir_path) 
                file.close()
                end_package_dir_path = [folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")]
                start_package_dir_path = set(start_package_dir_path)
                start_package_dir_path.add("h")
                end_package_dir_path = set(end_package_dir_path)
                end_package_dir_path.add("h")
                name = list(end_package_dir_path - start_package_dir_path)[0]
                if not self.list.check_exits(name=name):
                    
                    dir_path = f"{self.current_directory}/packages"
                    file = tarfile.open(path) 
                    file.extractall(dir_path) 
                    file.close()
                    
                    check_call([sys.executable, "-m", "pip", "install", "-r", f"{self.current_directory}/packages/{name}/requirements.txt"], shell=False)
                    
                    # move template folder
                    package_templates_dir = f"{self.current_directory}/templates/{name}"
                    shutil.copytree(f"{dir_path}/{name}/templates", package_templates_dir)
                    shutil.rmtree(f"{dir_path}/{name}/templates")
                    
                    # move static folder
                    package_static_dir = f"{self.current_directory}/static/{name}"
                    shutil.copytree(f"{dir_path}/{name}/static", package_static_dir)
                    shutil.rmtree(f"{dir_path}/{name}/static")
                    
                    # Get properties from package.ini
                    package_config = configparser.ConfigParser()
                    package_config.read(f"{dir_path}/{name}/package.ini")
                            
                    self.list.add_package_to_list(package_config=package_config)
                    print(Fore.GREEN + f"Packag {name} imported")
                else:
                    print(Fore.RED + "Package alredy installed")
                shutil.rmtree(f"{self.current_directory}/temp/{name}")
            else:
                print(Fore.RED + "File not found")
        
    
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
                        pass
                    else:
                        if not self.list.check_exits(package_name):
                            # add package to list
                            self.list.add_package_to_list(package_config=package_config)
                            # move templates dir
                            package_template_folder = f"{self.current_directory}/templates/{package_name}"
                            shutil.copytree(f"{package_dir_path}/templates", package_template_folder)
                            shutil.rmtree(f"{package_dir_path}/templates")
                            # move static dir
                            package_template_folder = f"{self.current_directory}/static/{package_name}"
                            shutil.copytree(f"{package_dir_path}/static", package_template_folder)
                            shutil.rmtree(f"{package_dir_path}/static")
                            # move dir to packages
                            shutil.move(package_dir_path, f"{self.current_directory}/packages")
                            # Install requirements python libs
                            check_call([sys.executable, "-m", "pip", "install", "-r", f"{self.current_directory}/packages/{package_name}/requirements.txt"], shell=False)
                            print(Fore.GREEN + f"Package {package_name} installed")
                        else:
                            print(Fore.RED + "\nPackage alredy exits")          
                else:
                    print(Fore.RED + "\nInvalid package")
            else:
                print(Fore.RED + "\nPackage does not contain package.ini")
        else:
            print(Fore.RED + "Url not valid")
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
            name = name.lower()
            # If name == "*" then remove all packages
            if name == "*":
                # Geting all packages from packages directory
                dir_path = f"{self.current_directory}/packages"
                packages = [folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")]
                # Removing packages
                for package in packages:
                    check_call([sys.executable, "-m", "pip", "uninstall", "-r", f"{self.current_directory}/packages/{package}/requirements.txt"], shell=False)
                    self.list.remove_package_from_list(name=package)
                    shutil.rmtree(f"{self.current_directory}/packages/{package}")
                    shutil.rmtree(f"{self.current_directory}/templates/{package}")
                    shutil.rmtree(f"{self.current_directory}/static/{package}")
                    print(Fore.GREEN + f"Package {package} removed")
                break
            
            # remove package if package in packages.ini
            elif self.list.check_exits(name=name):
                check_call([sys.executable, "-m", "pip", "uninstall", "-r", f"{self.current_directory}/packages/{name}/requirements.txt"], shell=False)
                if os.path.exists(f"{self.current_directory}/packages/{name}"):
                    shutil.rmtree(f"{self.current_directory}/packages/{name}")
                if os.path.exists(f"{self.current_directory}/templates/{name}"):
                    shutil.rmtree(f"{self.current_directory}/templates/{name}")
                if os.path.exists(f"{self.current_directory}/static/{name}"):
                    shutil.rmtree(f"{self.current_directory}/static/{name}")
                self.list.remove_package_from_list(name=name)
                print(Fore.GREEN + f"Package {name} removed")
            
            # package not found
            else:
                print(Fore.RED + "Package not found")
    
    # create package
    def create(self, names:list[str]) -> None:
        for name in names:
            name = name.lower()
            package_version = "0.0.1"
            # Check on not exist package in packages.ini file
            if not self.list.check_exits(name):
                
                # Creating package folder
                os.makedirs(f"{self.current_directory}/packages/{name}")
                os.makedirs(f"{self.current_directory}/templates/{name}")
                os.makedirs(f"{self.current_directory}/static/{name}")
                
                # creating new package.ini file
                with open(f"{self.current_directory}/packages/{name}/package.ini", "w") as ini_file:
                    ini_file.write(f"[INFO]")
                    ini_file.write(f"\nname = {name}")
                    ini_file.write(f"\nversion = {package_version}")
                
                # creating new requirements file
                with open(f"{self.current_directory}/packages/{name}/requirements.txt", "w") as ini_file:
                    pass
                
                # Add package to packages.ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{name}/package.ini")
                self.list.add_package_to_list(package_config=package_config)
                print(Fore.GREEN + f"Package {name} created")
            else:
                print(Fore.RED + "Package alredy exits")

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
    
    # Import python lib
    @staticmethod
    def import_or_install_pylib(package):
        try:
            importlib.import_module(package)
        except ImportError:
            try:
                check_call([sys.executable, '-m', 'pip', 'install', package], shell=False)
            except:
                pass
        try:
            module = importlib.import_module(package)
            globals()[package] = module
        except ImportError:
            pass
        
    # run server
    def run(self, package:str=None) -> None:
        app = Flask("United Systems Core",
                    template_folder=f'{self.current_directory}/templates',
                    static_folder=f'{self.current_directory}/static')
        
        # Get packages for running
        packages_folder = f"{self.current_directory}/packages"
        packages = [
                    package for package in os.listdir(packages_folder) 
                    if os.path.isdir(f"{packages_folder}/{package}")
                    ] if package == None else package.split(",")
        
        # Importing packages modules
        for package in packages:
            package_folder = f"{self.current_directory}/packages/{package}"
            package_files = [package for package in os.listdir(package_folder) 
                             if (".py" in package) and (not package.startswith('__'))]
            for package_file in package_files:
                package_module = importlib.util.spec_from_file_location(package_file.replace(".py", ""), f"{package_folder}/{package_file}")
                package = importlib.util.module_from_spec(package_module)
                try:
                    package_module.loader.exec_module(package)
                except ModuleNotFoundError as e:
                    self.import_or_install_pylib(e.name)
                    
                # check import 
                try:
                    package_module = importlib.util.spec_from_file_location(package_file.replace(".py", ""), f"{package_folder}/{package_file}")
                    package = importlib.util.module_from_spec(package_module)
                    package_module.loader.exec_module(package)
                except ModuleNotFoundError as e:
                    print(Fore.YELLOW + f"Package not run because module '{e.name}' was not found in {package} package")
                    break
                
                getattr(package, "main")(app)
                    
                    
                    
                
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
                pack_static_dir = f"{self.current_directory}/static/{name}"
                try:
                    # Creating temp temoplates file in package folder
                    shutil.copytree(pack_templates_dir, f"{pack_dir}/templates")
                    shutil.copytree(pack_static_dir, f"{pack_dir}/static")
                    
                    # creating tar.gz file
                    with tarfile.open(f"{os.getcwd()}/{name}.tar.gz", "w:gz") as tar:
                        tar.add(pack_dir, arcname=os.path.basename(pack_dir))
                        
                    # Removing temp temoplates file in package folder
                    shutil.rmtree(f"{pack_dir}/templates")
                    shutil.rmtree(f"{pack_dir}/static")
                    print(Fore.GREEN + "Package exported")
                    
                except Exception as e:
                    print(Fore.RED + f"Error:\n{e}")
            else:
                print(Fore.RED + "Package not found")
            
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
                    print(Fore.GREEN + "Opened with VS Code")
                # vim
                elif shutil.which('vim') != None:
                    Popen([shutil.which('vim'), pack_dir], shell=False)
                    print(Fore.GREEN + "Opened with Vim")
                # no ide
                else:
                    print(Fore.RED + "IDE not found")
                
            else:
                # Manually getting the IDE
                ide = ide.replace("--", "")
                # vscode
                if ide == "vscode":
                    if shutil.which('code') != None:
                        Popen([shutil.which('code'), pack_dir], shell=False)
                        print(Fore.GREEN + "Opened with VS Code")
                    else:
                        print(Fore.RED + "VS Code not found")
                # vim
                elif ide == "vim":
                    if shutil.which('vim') != None:
                        Popen([shutil.which('vim'), pack_dir], shell=False)
                        print(Fore.GREEN + "Opened with Vim")
                    else:
                        print(Fore.RED + "Vim not found")
                # no ide
                else:
                    print(Fore.RED + "IDE not selected")
        else:
            print(Fore.RED + "Package not found")
            
    def templates(self, package:str=None) -> None:
        if package != None:
            package = package.lower()
            if self.list.check_exits(package):
                path = f"{self.current_directory}/templates/{package}"
            else:
                print(Fore.RED + "Package not found")
                return None
        else:
            path = f"{self.current_directory}/templates"
            
        # Open templates folder
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            Popen(["open", path])
        else:
            Popen(["xdg-open", path])
            
    def static(self, package:str=None) -> None:
        if package != None:
            package = package.lower()
            if self.list.check_exits(package):
                path = f"{self.current_directory}/static/{package}"
            else:
                print(Fore.RED + "Package not found")
                return None
        else:
            path = f"{self.current_directory}/static"
            
        # Open templates folder
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
        packages_files = [
            file.lower() for file in os.listdir(f"{self.current_directory}/packages") 
            if os.path.isdir(f"{self.current_directory}/packages/{file.lower()}")
            ]
        templates_files = [
            file.lower() for file in os.listdir(f"{self.current_directory}/packages") 
            if os.path.isdir(f"{self.current_directory}/packages/{file.lower()}")
            ]
        static_files = [
            file.lower() for file in os.listdir(f"{self.current_directory}/packages") 
            if os.path.isdir(f"{self.current_directory}/packages/{file.lower()}")
            ]
        
        files = set(packages_files).union(templates_files).union(static_files)
        
        for file in files:
            # Checking exist package.ini file
            if os.path.exists(f"{self.current_directory}/packages/{file}/package.ini"):
                
                # Open packages ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{file}/package.ini")
                
                # checking templates folder
                if not os.path.exists(f"{self.current_directory}/templates/{file}"):
                    os.mkdir(f"{self.current_directory}/templates/{file}")
                
                # checking static folder
                if not os.path.exists(f"{self.current_directory}/static/{file}"):
                    os.mkdir(f"{self.current_directory}/static/{file}")
                    
                check_call([sys.executable, "-m", "pip", "install", "-r", f"{self.current_directory}/packages/{file}/requirements.txt"], shell=False)
                    
                # Add package to list 
                self.list.add_package_to_list(package_config=package_config)
            else:
                # remove folder
                if os.path.exists(f"{self.current_directory}/packages/{file.lower()}"):
                    shutil.rmtree(f"{self.current_directory}/packages/{file.lower()}")
                if os.path.exists(f"{self.current_directory}/templates/{file.lower()}"):
                    shutil.rmtree(f"{self.current_directory}/templates/{file.lower()}")
                if os.path.exists(f"{self.current_directory}/static/{file.lower()}"):
                    shutil.rmtree(f"{self.current_directory}/static/{file.lower()}")
              
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
                
        # Restor static file 
        new_static_files = [file for file in os.listdir(f"{dir_path}/update/usc/static")]
        for file in new_static_files :
            full_path = os.path.join(f"{dir_path}/update/usc/static", file)
            if os.path.isdir(full_path):
                shutil.copytree(full_path, f"{self.current_directory}/static")
            else:
                shutil.copy2(full_path, f"{self.current_directory}/static")
                
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
        
        print(Fore.GREEN + "Latest version installed")
                
                
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
                        print(Fore.RED + "Latest version already installed")
        else:
            print(Fore.RED + "Url not valid")
            
    @staticmethod
    def help_message() -> dict:
        message_data = {
            "install": "Install package from USCServer and GitHub",
            "import": "Import a package from tar.gz file",
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
    
    @staticmethod
    def core_version():
        with open(f'{os.path.dirname(os.path.abspath(__file__))}/version', "r") as ver:
            version = ver.read()
        preview_text = Figlet(font='larry3d')
        print(preview_text.renderText('------'))
        print(preview_text.renderText(f'V-{version}'))
        print(preview_text.renderText('------'))