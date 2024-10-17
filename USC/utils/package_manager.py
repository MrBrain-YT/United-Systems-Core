# PackageManager class for usc methods

import os
import configparser
import shutil
import requests
import re
import tarfile
import stat
import sys
from subprocess import call, Popen, check_call
import importlib
import platform
import ipaddress
from multiprocessing import Process
import signal

import git
from colorama import Fore
from pyfiglet import Figlet
from tqdm import tqdm
from flask import Flask
from terminaltables import AsciiTable

from utils.list_work import ListWorker
import utils.prerun_worker as prerun_worker # working during import
from utils.MicroConsole.micro_console import MicroConsole, MicroLog


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
        self.stdout = sys.stdout
    
    # install package algorithm
    def install_algorithm(self, dir_path, name, is_hiden:bool):
        # check os compatibility
        package_config = configparser.ConfigParser()
        package_files_path = f"{dir_path}/{name}"
        config_patch = f"{package_files_path}/package.ini"
        if (os.path.exists(config_patch)):
            package_config.read(config_patch)
        
            if (package_config["INFO"].get("os").lower() == "any" or package_config["INFO"].get("os").lower() == platform.system().lower()):
                pass
            else:
                while True:
                    sys.stdout = self.stdout
                    agree = input(Fore.RED + "The package is not compatible with your operating system, install it anyway (Y/n): " + Fore.RESET).lower()
                    sys.stdout = open(os.devnull, "w")
                    if agree == "y": 
                        break
                    elif agree == "n":
                        shutil.rmtree(dir_path)
                        return 0
                    else: continue
                    
            # install usc packages    
            require_usc = f"{package_files_path}/requirements.usc"
            if os.path.exists(require_usc):
                with open(require_usc, "r") as require:
                    text = require.read().replace("\n", "").replace(" ", "")
                if text != "":
                    only_install = False
                    for package in text.split("\n"):
                        install_state = self.install(package, is_hiden=True)
                        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
                        if not install_state:
                            sys.stdout = self.stdout
                            print(f"{Fore.RED}Dependency package '{package.split("==")[0]}' cannot be installed{Fore.RESET}")
                            sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
                            while True and not only_install:
                                sys.stdout = self.stdout
                                agree = input(Fore.RED + "Dependency package is not installed, install package it anyway (Y/n): " + Fore.RESET).lower()
                                sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
                                if agree == "y": 
                                    only_install = True
                                    break
                                elif agree == "n":
                                    with open(f"{package_files_path}/requirements.usc", "r") as require:
                                        for line in require.read().split("\n"):
                                            if line != "":
                                                self.remove([line.split("==")[0]], is_hiden=True)
                                    shutil.rmtree(f"{self.current_directory}/temp/{name}")
                                    return 0
                                else: continue
                            
            # install python packages
            require_txt = f"{package_files_path}/requirements.txt"
            with open(require_txt, "r") as require:
                text = require.read().replace("\n", "").replace(" ", "")
            if text != "":
                check_call([sys.executable, "-m", "pip", "install", "-r", require_txt], shell=False)
                
            # move template folder
            package_templates_dir = f"{self.current_directory}/templates/{name}"
            shutil.copytree(f"{package_files_path}/templates", package_templates_dir)
            shutil.rmtree(f"{package_files_path}/templates")
            
            # move static folder
            package_static_dir = f"{self.current_directory}/static/{name}"
            shutil.copytree(f"{package_files_path}/static", package_static_dir)
            shutil.rmtree(f"{package_files_path}/static")
            
            # move package folder
            package_dir = f"{self.current_directory}/packages/{name}"
            shutil.copytree(f"{package_files_path}", package_dir)
            shutil.rmtree(f"{package_files_path}")
                
            self.list.add_package_to_list(package_config=package_config)    
            
            print(Fore.GREEN + f"Package {name} installed" + Fore.RESET)
        else:
            print(Fore.RED + "package.ini file not found" + Fore.RESET) 
        
    
    # install package
    def install(self, name:str, is_hiden:bool=False) -> None:
        # run in hide mode
        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
        
        _name, name = name ,name.split("==")[0].lower()
        print(not self.list.check_exits(name) and name not in [file for file in os.listdir(f"{self.current_directory}/packages") if file != "packages.ini"])
        if not self.list.check_exits(name) and name not in [file for file in os.listdir(f"{self.current_directory}/packages") if file != "packages.ini"]:
            name = name.lower()
            # Get download server info from run.ini
            server_config = configparser.ConfigParser()
            server_config.read(f"{self.current_directory}/run.ini") 
            host = server_config["DOWNLOAD"].get("host")
            port = server_config["DOWNLOAD"].get("port")
            # Get package
            data = {
                "package_name" : name,
                "version" : "none" if len(_name.split("==")) == 1 else _name.split("==")[1]
                }
            try:
                response = requests.post(url=f"http://{host}:{port}/package", data=data)
                # Checking valid server data
                if response.status_code == 200:
                    # Get tar-gz file from server
                    filename = f'{self.current_directory}/temp/{name}.tar.gz'
                    if not is_hiden:
                        total_size = int(response.headers.get('content-length', 0))
                        with open(filename, 'wb') as f, tqdm(
                            total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
                            desc=f"Downloading {name} ", initial=0, miniters=1) as bar:
                            for data in response.iter_content(chunk_size=1024):
                                size = f.write(data)
                                bar.update(size)
                    else:
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                            
                    # extracting file
                    dir_path = f"{self.current_directory}/temp/"
                    file = tarfile.open(filename) 
                    file.extractall(dir_path) 
                    file.close()
                    os.remove(filename)
                    
                    # install package
                    self.install_algorithm(dir_path=dir_path, name=name, is_hiden=is_hiden)
                    return True
                                    
                elif response.status_code == 404:
                    print(Fore.RED + f"Package '{name}' not found in server" + Fore.RESET)
                    return False
                elif response.status_code == 405:
                    dir_path = f"{self.current_directory}/temp/"
                    while True:
                        sys.stdout = self.stdout
                        agree = input(Fore.RED + f"The package '{name}' is available on the server, but not this version, install it anyway (Y/n): " + Fore.RESET).lower()
                        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
                        if agree == "y": 
                            self.install(name=name, is_hiden=True)
                            break
                        elif agree == "n":
                            if os.path.exists(f"{dir_path}/{os.listdir(dir_path)[0]}/{name}/requirements.usc"):
                                with open(f"{dir_path}/{os.listdir(dir_path)[0]}/{name}/requirements.usc", "r") as require:
                                    for line in require.read().split("\n"):
                                        if line != "":
                                            self.remove([line.split("==")[0]], is_hiden=True)
                                    shutil.rmtree(f"{self.current_directory}/temp/{name}")
                            return 0
                        else: continue
                        
            except KeyboardInterrupt:
                print(Fore.YELLOW + "Ctrl+C" + Fore.RESET)
                return False
            
            except requests.exceptions.ConnectionError:
                print(Fore.RED + "No internet access" + Fore.RESET)
                return False
        else:
            print(Fore.RED + f"Package '{name}' alredy exist" + Fore.RESET)
            return True
        
        sys.stdout = self.stdout
            
    # import package
    def import_package(self, paths:list, is_hiden:bool=False) -> None:
        # run in hide mode
        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
        
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
                    # install package
                    dir_path = f"{self.current_directory}/temp/{name}"
                    self.install_algorithm(dir_path=dir_path, name=name, is_hiden=is_hiden)
                else:
                    print(Fore.RED + "Package alredy installed" + Fore.RESET)
                shutil.rmtree(f"{self.current_directory}/temp/{name}")
            else:
                print(Fore.RED + "File not found" + Fore.RESET)
        
        sys.stdout = self.stdout
        self.refresh()
    
    @staticmethod
    def on_rm_error(func, path, exc_info) -> None:
        #from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
    
    # install package from git 
    def install_git(self, url:str, is_hiden:bool=False) -> None:
        # run in hide mode
        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
        
        dir_path = f'{self.current_directory}/temp/git'
        code = requests.get(url).status_code
        if code == 200:
            # Clone repo from using URL
            git.Repo.clone_from(url, dir_path, progress=Progress())
            
            # Check package
            package_dir_path = f"{dir_path}/{[folder for folder in os.listdir(dir_path) if folder != ".git" and os.path.isdir(f"{dir_path}/{folder}")][0]}"
            if os.path.exists(f"{package_dir_path}/package.ini"):
                package_config = configparser.ConfigParser()
                package_config.read(f"{package_dir_path}/package.ini")
                package_name = package_config["INFO"].get("name")
                package_version = package_config["INFO"].get("version")
                package_os = package_config["INFO"].get("os")
                if package_name and package_version != None and package_os != None:
                    pattern = r"[!@#$%^&*(),?\":{}|<>]"
                    if re.search(pattern, package_name) or re.search(pattern, package_version):
                        pass
                    else:
                        if not self.list.check_exits(package_name):
                            # check os compatibility
                            if (package_os.lower() == "any" or package_os.lower() == platform.system().lower()):
                                pass
                            else:
                                while True:
                                    sys.stdout = self.stdout
                                    agree = input(Fore.RED + "The package is not compatible with your operating system, install it anyway (Y/n): " + Fore.RESET).lower()
                                    sys.stdout = open(os.devnull, "w")
                                    if agree == "y": break
                                    elif agree == "n":
                                        shutil.rmtree(dir_path)
                                        return 0
                                    else: continue
                            
                            # Install requirements python libs
                            require_txt = f"{dir_path}/{package_name}/requirements.txt"
                            with open(require_txt, "r") as require:
                                text = require.read().replace("\n", "").replace(" ", "")
                            if text != "":
                                check_call([sys.executable, "-m", "pip", "install", "-r", f"{package_dir_path}/requirements.txt"], shell=False)
                                
                            # install usc packages
                            require_usc = f"{dir_path}/{package_name}/requirements.usc"
                            if os.path.exists(require_usc):
                                with open(require_usc, "r") as require:
                                    text = require.read().replace("\n", "").replace(" ", "")
                                if text != "":
                                    for package in text.split("\n"):
                                        install_state = self.install(package, is_hiden=True)
                                        if not install_state:
                                            sys.stdout = self.stdout
                                            print(f"{Fore.RED}Dependency package '{package.split("==")[0]}' cannot be installed{Fore.RESET}")
                                            sys.stdout = open(os.devnull, "w")
                                            while True and not only_install:
                                                sys.stdout = self.stdout
                                                agree = input(Fore.RED + "Dependency package is not installed, install package it anyway (Y/n): " + Fore.RESET).lower()
                                                sys.stdout = open(os.devnull, "w")
                                                if agree == "y": 
                                                    only_install = True
                                                    break
                                                elif agree == "n":
                                                    with open(f"{dir_path}/{package_name}/requirements.usc", "r") as require:
                                                        for line in require.read().split("\n"):
                                                            if line != "":
                                                                self.remove([line.split("==")[0]], is_hiden=True)
                                                    shutil.rmtree(f"{self.current_directory}/temp/{package_name}")
                                                    return 0
                                                else: continue
                               
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
                            # add package to list
                            self.list.add_package_to_list(package_config=package_config)
                            print(Fore.GREEN + f"Package {package_name} installed" + Fore.RESET)
                        else:
                            print(Fore.RED + "\nPackage alredy exits" + Fore.RESET)
                else:
                    print(Fore.RED + "\nInvalid package" + Fore.RESET)
            else:
                print(Fore.RED + "\nPackage does not contain package.ini" + Fore.RESET)
        else:
            print(Fore.RED + "Url not valid" + Fore.RESET)
            return None

        # delete .git folder
        if platform.system() == "Windows":
            for i in os.listdir(dir_path):
                if i.endswith('git'):
                    tmp = os.path.join(dir_path, i)
                    # We want to unhide the .git folder before unlinking it.
                    while True:
                        call(['attrib', '-H', tmp])
                        break
                    shutil.rmtree(tmp, onexc=self.on_rm_error)
                    shutil.rmtree(dir_path)
        else:
            pass
            call(['rm', '-rf', dir_path])

        sys.stdout = self.stdout
        self.refresh()
    
    # remove package 
    def remove(self, names:list[str], is_hiden:bool=False) -> None:
        # run in hide mode
        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
        
        for name in names:
            name = name.lower()
            # If name == "*" then remove all packages
            if name == "*":
                # Geting all packages from packages directory
                dir_path = f"{self.current_directory}/packages"
                packages = [folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")]
                # Removing packages
                for package in packages:
                    
                    with open(f"{self.current_directory}/packages/{package}/requirements.txt", "r") as require:
                        text = require.read().replace("\n", "").replace(" ", "")
                    if text != "":
                        check_call([sys.executable, "-m", "pip", "uninstall", "-r", f"{self.current_directory}/packages/{package}/requirements.txt"], shell=False)
                        
                    self.list.remove_package_from_list(name=package)
                    shutil.rmtree(f"{self.current_directory}/packages/{package}")
                    shutil.rmtree(f"{self.current_directory}/templates/{package}")
                    shutil.rmtree(f"{self.current_directory}/static/{package}")
                    print(Fore.GREEN + f"Package {package} removed" + Fore.RESET)
                break
            
            # remove package if package in packages.ini
            elif self.list.check_exits(name=name):
                # remove python requirements
                with open(f"{self.current_directory}/packages/{name}/requirements.txt", "r") as require:
                        text = require.read().replace("\n", "").replace(" ", "")
                if text != "":
                    check_call([sys.executable, "-m", "pip", "uninstall", "-r", f"{self.current_directory}/packages/{name}/requirements.txt"], shell=False)
                
                # remove usc requirements
                if os.path.exists(f"{self.current_directory}/packages/{name}/requirements.usc"):
                    with open(f"{self.current_directory}/packages/{name}/requirements.usc", "r") as require:
                            text = require.read().replace("\n", "").replace(" ", "")
                    if text != "":
                        for package in text.split("\n"):
                            self.remove([package.split("==")[0]], is_hiden=True)
                            sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
                        
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
                print(Fore.RED + f"Package {name} not found" + Fore.RESET)

        sys.stdout = self.stdout
        
    # create package
    def create(self, names:list[str], is_hiden:bool=False) -> None:
        # run in hide mode
        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
        
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
                    ini_file.write(f"\nos = any")
                    ini_file.write(f"\nport = 5000")
                
                # creating new python requirements file
                with open(f"{self.current_directory}/packages/{name}/requirements.txt", "w"):
                    pass
                
                # creating new usc requirements file
                with open(f"{self.current_directory}/packages/{name}/requirements.usc", "w"):
                    pass
                
                # creating new example python file
                with open(f"{self.current_directory}/packages/{name}/main.py", "w") as py_file:
                    # f"    def home_page_{secrets.token_hex(16)}():\n" +\
                    text = "from flask import Flask\n\n\n" +\
                        "def main(app:Flask):\n\n" +\
                        f"    @app.route('/{name}/', methods = ['GET'], endpoint='{name}_home_page')\n" +\
                        f"    def home_page():\n" +\
                        f'        return "Home page for {name} package"'
                    py_file.write(text)
                
                # Add package to packages.ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{name}/package.ini")
                self.list.add_package_to_list(package_config=package_config)
                print(Fore.GREEN + f"Package {name} created" + Fore.RESET)
            else:
                print(Fore.RED + "Package alredy exits" + Fore.RESET)
                
        sys.stdout = self.stdout

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
    
    @staticmethod
    def run_algorithm(current_directory, port, ports_config, status):
        
        # close signal handler
        def handle_sigint(signum, frame):
            pass
        signal.signal(signal.SIGINT, handle_sigint)
        
        # init logger
        log = MicroLog()
        
        # create flask app
        app = Flask(f"USCore {"public" if status else "private"} {port}",
            template_folder=f'{current_directory}/templates',
            static_folder=f'{current_directory}/static')
        
        # Importing packages modules
        for package in ports_config[port]:
            package = package
            package_folder = f"{current_directory}/packages/{package}"
            package_files = [package for package in os.listdir(package_folder) 
                            if ".py" in package or ".pyc" in package]
            for package_file in package_files:
                # import package python modules
                try:
                    package_module = importlib.util.spec_from_file_location(package_file.replace(".py", "") if ".pyc" not in package_file else package_file.replace(".pyc", ""), f"{package_folder}/{package_file}")
                    package = importlib.util.module_from_spec(package_module)
                    package_module.loader.exec_module(package)
                # except ModuleNotFoundError as e:
                #     log.add_warnings([f"Module not run because in module '{e.name}' was not found in {package}"])
                    
                except Exception as error:
                    log.add_warnings([f"{package_folder}/{package_file}|" + f"{package}|" + str(error) + "\n"])
                    
                
                if (hasattr(package, "main")):
                    try:
                        getattr(package, "main")(app)
                    except Exception as error:
                        log.add_errors([f"{package_folder}/{package_file}|" + f"{package}|" + str(error) + "\n"])
                else:
                    pass
        
        if status:
            # run server using data from run.ini
            server_config = configparser.ConfigParser()
            server_config.read(f"{current_directory}/run.ini")
            host = server_config["SERVER"].get("host")
        else:
            host = "localhost"
        app.run(host=host, port=port)

    # run server
    def run(self, line_packages:str=None, ignore:bool=False) -> None: 
        MicroLog().clear_log()
        # self.refresh()
        
        # Get packages for running
        packages_config = configparser.ConfigParser()
        packages_config.read(f"{self.current_directory}/packages/packages.ini")
        ports_config = {}
        # if packages not choiced (automatic find)
        if line_packages is None and not ignore:
            for package_name in packages_config.sections():
                package_port = packages_config[package_name]["port"]
                if package_port in ports_config.keys():
                    ports_config[package_port].append(package_name)
                else:
                    ports_config[package_port] = [package_name]
                    
        # ignore all packages
        elif line_packages is None and ignore:
            pass
        
        # if packages choiced and not ignored (manual find)
        elif line_packages is not None and not ignore:
            packages = line_packages.split(",")
            for index, package in enumerate(packages):
                packages[index] = package.replace(" ", "")
                
            for package_name in packages_config.sections():
                if package_name in packages:
                    package_port = packages_config[package_name]["port"]
                    if package_port in ports_config.keys():
                        ports_config[package_port].append(package_name)
                    else:
                        ports_config[package_port] = [package_name]
                        
        # if packages choiced and ignored (manual find)
        elif line_packages is not None and ignore:
            packages = line_packages.split(",")
            for index, package in enumerate(packages):
                packages[index] = package.replace(" ", "")
                
            for package_name in packages_config.sections():
                if package_name not in packages:
                    package_port = packages_config[package_name]["port"]
                    if package_port in ports_config.keys():
                        ports_config[package_port].append(package_name)
                    else:
                        ports_config[package_port] = [package_name]
        
        # sorting microservices
        private_services = {}
        public_services = {}
        for port in ports_config.keys():
            for package in ports_config[port]:
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{package.lower()}/package.ini")
                if package_config["INFO"].get("status") == "public":
                    if public_services.get(port) is None:
                        public_services[port] = []
                        public_services[port].append(package)
                    else:
                        public_services[port].append(package)
                else:
                    if private_services.get(port) is None:
                        private_services[port] = []
                        private_services[port].append(package)
                    else:
                        private_services[port].append(package)
        
        # run MicroConsole    
        max_services = len(public_services) + len(private_services)
        MConsole = MicroConsole(PackageManager=self, ports_config=ports_config, max_services=max_services, 
                                public_services=public_services, private_services=private_services)
        
        # run microservices
        process_config = {}
        for port in public_services.keys():
            microsevice = Process(target=self.run_algorithm, args=(self.current_directory, port, public_services, True), name=f"USCore public {port}")
            microsevice.start()
            MConsole.next_init_bar()
            # add to process config
            if process_config.get(port) is None:
                process_config[port] = {}
                process_config[port]["public"] = microsevice
            else:
                process_config[port]["public"] = microsevice
            
        for port in private_services.keys():
            microsevice = Process(target=self.run_algorithm, args=(self.current_directory, port, private_services, False), name=f"USCore private {port}")
            microsevice.start()
            MConsole.next_init_bar()
            # add to process config
            if process_config.get(port) is None:
                process_config[port] = {}
                process_config[port]["private"] = microsevice
            else:
                process_config[port]["private"] = microsevice
            
        MConsole.init_services_config(process_config=process_config, public_services=public_services, private_services=private_services)
        MConsole.work_cycle() 

    # export package
    def export(self, names:list[str], path:str=None, is_hiden:bool=False) -> None:
        # run in hide mode
        sys.stdout = open(os.devnull, "w") if is_hiden else self.stdout
        
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
                    if path is None:
                        with tarfile.open(f"{os.getcwd()}/{name}.tar.gz", "w:gz") as tar:
                            tar.add(pack_dir, arcname=os.path.basename(pack_dir))
                    else:
                        with tarfile.open(f"{path}/{name}.tar.gz", "w:gz") as tar:
                            tar.add(pack_dir, arcname=os.path.basename(pack_dir))
                        
                    # Removing temp temoplates file in package folder
                    shutil.rmtree(f"{pack_dir}/templates")
                    shutil.rmtree(f"{pack_dir}/static")
                    print(Fore.GREEN + f"Package {name} exported" + Fore.RESET)
                    
                except Exception as e:
                    print(Fore.RED + f"Error:\n{e}" + Fore.RESET)
            else:
                print(Fore.RED + f"Package {name} not found" + Fore.RESET)
        
        sys.stdout = self.stdout
            
    # open package in IDE
    def code(self, name:str, ide:str=None, no_package:bool=False):
        if self.list.check_exits(name=name) or no_package:
            pack_dir = f"{self.current_directory}/packages/{name}" \
                if no_package == False else f"{self.current_directory}/packages/"
                
            # Automatic get IDE
            if ide is None:
                # vscode
                if shutil.which('code') != None:
                    Popen([shutil.which('code'), pack_dir], shell=False)
                    print(Fore.GREEN + "Opened with VS Code" + Fore.RESET)
                # vim
                elif shutil.which('vim') != None:
                    Popen([shutil.which('vim'), pack_dir], shell=False)
                    print(Fore.GREEN + "Opened with Vim" + Fore.RESET)
                # no ide
                else:
                    print(Fore.RED + "IDE not found" + Fore.RESET)
                
            else:
                # Manually getting the IDE
                ide = ide.replace("--", "")
                # vscode
                if ide == "vscode":
                    if shutil.which('code') != None:
                        Popen([shutil.which('code'), pack_dir], shell=False)
                        print(Fore.GREEN + "Opened with VS Code" + Fore.RESET)
                    else:
                        print(Fore.RED + "VS Code not found" + Fore.RESET)
                # vim
                elif ide == "vim":
                    if shutil.which('vim') != None:
                        Popen([shutil.which('vim'), pack_dir], shell=False)
                        print(Fore.GREEN + "Opened with Vim" + Fore.RESET)
                    else:
                        print(Fore.RED + "Vim not found" + Fore.RESET)
                # no ide
                else:
                    print(Fore.RED + "IDE not selected" + Fore.RESET)
        else:
            print(Fore.RED + "Package not found" + Fore.RESET)

    def templates(self, package:str=None) -> None:
        if package != None:
            package = package.lower()
            if self.list.check_exits(package):
                path = f"{self.current_directory}/templates/{package}"
            else:
                print(Fore.RED + "Package not found" + Fore.RESET)
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
                print(Fore.RED + "Package not found" + Fore.RESET)
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
    def set_server_config(self, read:bool, server_info:str, is_my_server:bool) -> None:
        config = configparser.ConfigParser()
        config.read(f'{self.current_directory}/run.ini')
        if read:
            if is_my_server:
                print(f"{Fore.LIGHTMAGENTA_EX}Server --> {config["SERVER"].get("host")}{Fore.RESET}")
            else:
                print(f"{Fore.LIGHTMAGENTA_EX}Download server --> {config["DOWNLOAD"].get("host")}:{config["DOWNLOAD"].get("port")}{Fore.RESET}")
        else:
            # Checking which parameter needs to be changing
            if is_my_server:
                host = server_info
                try:
                    ipaddress.ip_address(host)
                    config['SERVER'] = {'host': host}
                    with open(f'{self.current_directory}/run.ini', 'w') as configfile:
                        config.write(configfile)
                except ValueError:
                    print(f"{Fore.RED}Invalid IP address entered{Fore.RESET}")

            else:
                if len(server_info.split(":")) == 2:
                    host, port = server_info.split(":") 
                    if host.replace(" ", "") != "" and port.replace(" ", "") != "":
                        config['DOWNLOAD'] = {'host': host,
                                        'port': port}
                        with open(f'{self.current_directory}/run.ini', 'w') as configfile:
                            config.write(configfile)
                    else:
                        print(f"{Fore.RED}Incorrect parameters were entered{Fore.RESET}")
                else:
                    print(f"{Fore.RED}Incorrect parameters were entered{Fore.RESET}")
          
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
        
        for file in packages_files:
            # Checking exist package.ini file
            if os.path.exists(f"{self.current_directory}/packages/{file}/package.ini"):
                
                # Open package ini file
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{file}/package.ini")
                
                # checking templates folder
                if not os.path.exists(f"{self.current_directory}/templates/{file}"):
                    os.mkdir(f"{self.current_directory}/templates/{file}")
                
                # checking static folder
                if not os.path.exists(f"{self.current_directory}/static/{file}"):
                    os.mkdir(f"{self.current_directory}/static/{file}")

                # install python requirements
                with open(f"{self.current_directory}/packages/{file}/requirements.txt", "r") as require:
                        text = require.read().replace("\n", "").replace(" ", "")
                if text != "":
                    check_call([sys.executable, "-m", "pip", "install", "-r", f"{self.current_directory}/packages/{file}/requirements.txt"], shell=False)
                
                # install usc requirements
                if os.path.exists(f"{self.current_directory}/packages/{file}/requirements.usc"):
                    with open(f"{self.current_directory}/packages/{file}/requirements.usc", "r") as require:
                            text = require.read().replace("\n", "").replace(" ", "")
                    if text != "":
                        for package in text.split("\n"):
                            self.install(package, is_hiden=True)
                else:
                    with open(f"{self.current_directory}/packages/{file}/requirements.usc", "w") as require:
                        require.write("")
                    
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
                    
    @staticmethod
    def python_run(py_args:str):
        print(sys.executable + " " + py_args)
        os.system(sys.executable + " " + py_args)
                
              
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
        
        # Restor new directories
        new_directories = [file for file in os.listdir(f"{dir_path}/update/usc") if os.path.isdir(file)]
        for file in new_directories:
            shutil.copytree(f"{dir_path}/update/usc/{file}", self.current_directory)
            
        # Restor packages file 
        new_packages_files = [file for file in os.listdir(f"{dir_path}/update/usc/packages") if "packages.ini" != file]
        # backup and remove general packages
        old_packages_files = [file for file in os.listdir(f"{self.current_directory}/packages") if "packages.ini" != file]
        general_packages_files = set(new_packages_files).intersection(old_packages_files)
        self.export(general_packages_files, path=f"{self.current_directory}/backups")
        self.remove(general_packages_files)
            
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
        if platform.system() == "Windows":
            for i in os.listdir(f"{dir_path}/update"):
                if i.endswith('git'):
                    tmp = os.path.join(f"{dir_path}/update", i)
                    # We want to unhide the .git folder before unlinking it.
                    while True:
                        call(['attrib', '-H', tmp])
                        break
                    shutil.rmtree(tmp, onexc=self.on_rm_error)
                    shutil.rmtree(f"{dir_path}/update")
        else:
            # delete update folder
            call(['rm', '-rf', f"{dir_path}/update"])
            
        # refresh packages list for update old packages ( use backward compatibility )
        check_call([sys.executable, f'{self.current_directory}/usc.py', 'refresh'], shell=False)
        
        print(Fore.GREEN + "Latest version installed" + Fore.RESET)
                
                
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
                        print(Fore.RED + "Latest version already installed" + Fore.RESET)
        else:
            print(Fore.RED + "Url not valid" + Fore.RESET)
            
    @staticmethod
    def help_message() -> dict:
        message_data = {
            "install": "Install package from USCServer and GitHub",
            "import": "Import a package from tar.gz file",
            "remove": "Remove package",
            "python": "Launching UScore python interpreter",
            "refresh": "Refrash packages data",
            "list": "Get list installed packages",
            "update": "Upadate United Systems Core",
            "run": "Start the server with all packages or only with selected ones",
            "export": "Export package to curent opened in terminal folder",
            "code": "Open packages or package in IDE (vs code, vim)",
            "templates": "Open templates folder",
            "static": "Open folder for static files",
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