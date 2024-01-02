# PackageManager class for usc methods

import os
import time
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
from flask import Flask
from terminaltables import AsciiTable
from progress.bar import ShadyBar

from __list_work import ListWorker

class PackageManager():
    
    def __init__(self) -> None:
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.list = ListWorker()
    
    # install package
    def install(self, name:str) -> None:
        name = name.lower()
        
        if not self.list.check_exits(name):
            # Get package
            data = {
                "package_name" : name
                }
            responce = requests.post(url="http://127.0.0.1:5000/package", data=data)
            if responce.status_code == 200:
                with open(f'{os.path.dirname(os.path.abspath(__file__))}/temp/{name}.tar.gz', 'wb') as file:
                    file.write(responce.content)
                
                # extracting file
                dir_path = f"{os.path.dirname(os.path.abspath(__file__))}/packages"
                file = tarfile.open(f"{os.path.dirname(os.path.abspath(__file__))}/temp/{name}.tar.gz") 
                file.extractall(dir_path) 
                file.close()
                os.remove(f'{os.path.dirname(os.path.abspath(__file__))}/temp/{name}.tar.gz')
                
                # move template folder
                package_templates_dir = f"{os.path.dirname(os.path.abspath(__file__))}/templates/{name}"
                shutil.copytree(f"{dir_path}/{name}/templates", package_templates_dir)
                shutil.rmtree(f"{dir_path}/{name}/templates")
                
                # Get properties from package.ini
                package_config = configparser.ConfigParser()
                package_config.read(f"{dir_path}/{name}/package.ini")
                
                with ShadyBar('Installing', max=20) as bar:
                    for i in range(20):
                        time.sleep(0.1)
                        bar.next()
                        
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
        error = False
 
        dir_path = f'{os.path.dirname(os.path.abspath(__file__))}/temp/git'
        code = requests.get(url).status_code
        if code == 200:
            # Клонируем репозиторий по указанному URL
            git.Repo.clone_from(url, dir_path)
            
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
                        # add package to list
                        if not self.list.check_exits(package_name):
                            self.list.add_package_to_list(package_config=package_config)
                            # move dir to packages
                            
                            package_template_folder = f"{os.path.dirname(os.path.abspath(__file__))}/templates/{package_name}"
                            shutil.copytree(f"{package_dir_path}/templates", package_template_folder)
                            shutil.rmtree(f"{package_dir_path}/templates")
                            shutil.move(package_dir_path, f"{os.path.dirname(os.path.abspath(__file__))}/packages")
                        else:
                            print("Package alredy exits")
                            error = True             
                else:
                    error = True
            else:
                error = True
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
    
        if error:
            pass
        else:
            with ShadyBar('Installing', max=20) as bar:
                for i in range(20):
                    time.sleep(0.1)
                    bar.next()
    
    # remove package 
    def remove(self, name:str) -> None:
        if os.path.exists(f"{self.current_directory}/packages/{name}"):
            self.list.remove_package_from_list(name=name)
            shutil.rmtree(f"{self.current_directory}/packages/{name}")
            shutil.rmtree(f"{self.current_directory}/templates/{name}")
            print("Package removed")
        else:
            print("Package not found")
    
    # create package
    def create(self, name:str) -> None:
        package_version = "0.0.1"
        if not self.list.check_exits(name):
            os.makedirs(f"{self.current_directory}/packages/{name}")
            with open(f"{self.current_directory}/packages/{name}/package.ini", "w") as ini_file:
                ini_file.write(f"[INFO]")
                ini_file.write(f"\nname = {name}")
                ini_file.write(f"\nversion = {package_version}")
            package_config = configparser.ConfigParser()
            package_config.read(f"{self.current_directory}/packages/{name}/package.ini")
            os.makedirs(f"{self.current_directory}/templates/{name}")
            self.list.add_package_to_list(package_config=package_config)
        else:
            print("Package alredy exits")

    # get packages list
    def get_list(self) -> str:
        config = configparser.ConfigParser()
        config.read(f"{self.current_directory}/packages/packages.ini")
        table_data = [['Name', "Version"]]
        for pack in config.sections():
            table_data.append([
                config[pack].get("name"),
                config[pack].get("version")
            ])
        table = AsciiTable(table_data)
        return table.table
    
    # run server
    def run(self, package:str=None) -> None:
        app = Flask("United Systems Core", template_folder=f'{self.current_directory}/templates')
        
        packages_folder = f"{self.current_directory}/packages"
        packages = [package for package in os.listdir(packages_folder) if os.path.isdir(f"{packages_folder}/{package}")] if package == None else package.split(",")
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
    def export(self, name:str) -> None:
        if self.list.check_exits(name):
            pack_dir = f"{self.current_directory}/packages/{name}"
            pack_templates_dir = f"{self.current_directory}/templates/{name}"
            try:
                shutil.copytree(pack_templates_dir, f"{pack_dir}/templates")
                with tarfile.open(f"{os.getcwd()}/{name}.tar.gz", "w:gz") as tar:
                    tar.add(pack_dir, arcname=os.path.basename(pack_dir))
                shutil.rmtree(f"{pack_dir}/templates")
                print("Package exported")
            except Exception as e:
                print(f"Error:\n{e}")
        else:
            "Package not found"
            
    # open package in IDE
    def code(self, name:str, ide:str=None, no_package:bool=False) -> None:
        if self.list.check_exits(name=name) or no_package:
            pack_dir = f"{self.current_directory}/packages/{name}" if  no_package == False else f"{self.current_directory}/packages/"
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
        files = [file for file in os.listdir(f"{self.current_directory}/packages") if os.path.isdir(f"{self.current_directory}/packages/{file}")]
        for file in files:
            if os.path.exists(f"{self.current_directory}/packages/{file}/package.ini"):
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{file}/package.ini")
                self.list.add_package_to_list(package_config=package_config)
            else:
                with open(f"{self.current_directory}/packages/{file}/package.ini", "w") as file_version:
                    file_version.write(f"[INFO]")
                    file_version.write(f"\nname = {file}")
                    file_version.write("\nversion = 0.0.1")
                package_config = configparser.ConfigParser()
                package_config.read(f"{self.current_directory}/packages/{file}/package.ini")
                os.mkdir(f"{self.current_directory}/templates/{file}")
                self.list.add_package_to_list(package_config=package_config)