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
from subprocess import call

import git
from terminaltables import AsciiTable
from progress.bar import ShadyBar

from __list_work import ListWorker

class PackageManager():
    
    def __init__(self) -> None:
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.list = ListWorker(path=f"{self.current_directory}/__packages")
    
    def install(self, name:str) -> None:
        name = name.lower()
        
        # Get package
        data = {
            "package_name" : name
            }
        responce = requests.post(url="http://127.0.0.1:5000/package", data=data)
        with open(f'{os.path.dirname(os.path.abspath(__file__))}/temp/{name}.tar.gz', 'wb') as file:
            file.write(responce.content)
        
        # extracting file
        dir_path = f"{os.path.dirname(os.path.abspath(__file__))}/packages"
        file = tarfile.open(f"{os.path.dirname(os.path.abspath(__file__))}/temp/{name}.tar.gz") 
        file.extractall(dir_path) 
        file.close()
        os.remove(f'{os.path.dirname(os.path.abspath(__file__))}/temp/{name}.tar.gz')
        
        # Get properties from package.ini
        package_config = configparser.ConfigParser()
        package_config.read(f"{dir_path}/{name}/package.ini")
        
        
        with ShadyBar('Installing', max=20) as bar:
            for i in range(20):
                time.sleep(0.1)
                bar.next()
                
        self.list.add_package_to_list(package_config=package_config)
    
    @staticmethod
    def on_rm_error(func, path, exc_info):
        #from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
        os.chmod(path, stat.S_IWRITE)
        os.unlink(path)
        
    def install_git(self, url:str) -> None:
        error = False
        
        
                
        dir_path = f'{os.path.dirname(os.path.abspath(__file__))}/temp/git'
        # Клонируем репозиторий по указанному URL
        git.Repo.clone_from(url, dir_path)
        
        # Check package
        package_dir_path = f"{dir_path}/{[folder for folder in os.listdir(dir_path) if os.path.isdir(f"{dir_path}/{folder}")][1]}"
        if os.path.exists(f"{package_dir_path}/package.ini"):
            config = configparser.ConfigParser()
            config.read(f"{package_dir_path}/package.ini")
            package_name = config["INFO"].get("name")
            package_version = config["INFO"].get("version")
            if package_name and package_version != None:
                pattern = r"[!@#$%^&*(),.?\":{}|<>]"
                if not re.search(pattern, package_name) and not re.search(pattern, package_version):
                    # add package to list
                    config_file = f"{os.path.dirname(os.path.abspath(__file__))}/packages/packages.ini"
                    packages_config = configparser.ConfigParser()
                    packages_config.read(config_file)
                    if package_name in packages_config.sections():
                        packages_config[package_name] = {
                            "name" : package_name,
                            "version" : package_version
                        }
                        with open(config_file, 'w') as configfile:
                            packages_config.write(configfile)
                        
                        # move dir to packages
                        shutil.move(package_dir_path, f"{os.path.dirname(os.path.abspath(__file__))}/packages")
                    else:
                        error = True
                else:
                    error = True
            else:
                error = True
        else:
            error = True

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
    
            
    def uninstall(self, name:str) -> None:
        self.list.remove_package_from_list(name=name)
        shutil.rmtree(f"{self.current_directory}/packages/{name}")
        
    # Not worked 
    def create(self, name:str) -> None:
        package_version = "0.0.1"
        # self.list.add_package_to_list(name=name, version=package_version)
        # os.makedirs(f"{self.current_directory}/packages/{name}")
        # with open(f"{self.current_directory}/packages/{name}/version", "w") as version_file:
        #     version_file.write(package_version)

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
            
    
    def set_server_config(self, server_info:str, is_my_server:bool) -> None:
        config = configparser.ConfigParser()
        config.read(f'{self.current_directory}/run.ini')
        if is_my_server:
            host, port = server_info.split(":")
            config['SERVER'] = {'host': host,
                                'port': port}
            with open('run.ini', 'w') as configfile:
                config.write(configfile)
        else:
            host, port = server_info.split(":")
            config['DOWNLOAD'] = {'host': host,
                                'port': port}
            with open('run.ini', 'w') as configfile:
                config.write(configfile)
            
    # Not worked     
    def refresh(self) -> None:
        # get files from directory
        files = os.listdir(f"{self.current_directory}/packages")
        # versions = []
        # for file in files:
        #     if os.path.exists(f"{self.current_directory}/packages/{file}/version"):
        #         with open(f"{self.current_directory}/packages/{file}/version", "r") as file_version:
        #             versions.append(file_version.read())
        #     else:
        #         versions.append("0.0.1")
        #         with open(f"{self.current_directory}/packages/{file}/version", "w") as file_version:
        #             file_version.write("0.0.1")
        # # join flename and version
        # file_and_version = []
        # for index, file in enumerate(files):
        #     file_and_version.append(f"{file}=={versions[index]}")
            
        # with open(f"{self.current_directory}/__packages", "w") as file:
        #     file.write("\n".join(file_and_version))