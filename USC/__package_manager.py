import os
import time
import re
import configparser
import shutil

from __list_work import ListWorker
from progress.bar import ShadyBar

class PackageManager():
    
    def __init__(self) -> None:
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.list = ListWorker(path=f"{self.current_directory}/__packages")
    
    def install(self, name:str) -> None:
        with open(f"{self.current_directory}/__packages", "r") as file:
            text = file.readlines()
            lines = []
            for line in text:
                if re.search(name+r"==\d.\d.\d", string=line):
                    print("Package is already present")
                    break
            else:
                name = name.lower()
                with ShadyBar('Installing', max=20) as bar:
                    for i in range(20):
                        time.sleep(0.5)
                        bar.next()
                        
                os.makedirs(f"{self.current_directory}/packages/{name}")
                with open(f"{self.current_directory}/packages/{name}/{name}.pkg", "w") as file:
                    file.write("package installed")
                    
                package_version = "1.0.0"
                with open(f"{self.current_directory}/packages/{name}/version", "w") as version_file:
                    version_file.write(package_version)
                self.list.add_package_to_list(name=name, version=package_version)
                print(f"Library {name} successful installed.")
            
    def uninstall(self, name:str) -> None:
        self.list.remove_package_from_list(name=name)
        shutil.rmtree(f"{self.current_directory}/packages/{name}")
        
    def create(self, name:str) -> None:
        package_version = "0.0.1"
        self.list.add_package_to_list(name=name, version=package_version)
        os.makedirs(f"{self.current_directory}/packages/{name}")
        with open(f"{self.current_directory}/packages/{name}/version", "w") as version_file:
            version_file.write(package_version)

    def get_list(self) -> str:
        with open(f"{self.current_directory}/__packages", "r") as file:
            text = file.read()
        return text 
    
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
                
    def refresh(self) -> None:
        # get files from directory
        files = os.listdir(f"{self.current_directory}/packages")
        versions = []
        for file in files:
            if os.path.exists(f"{self.current_directory}/packages/{file}/version"):
                with open(f"{self.current_directory}/packages/{file}/version", "r") as file_version:
                    versions.append(file_version.read())
            else:
                versions.append("0.0.1")
                with open(f"{self.current_directory}/packages/{file}/version", "w") as file_version:
                    file_version.write("0.0.1")
        # join flename and version
        file_and_version = []
        for index, file in enumerate(files):
            file_and_version.append(f"{file}=={versions[index]}")
            
        with open(f"{self.current_directory}/__packages", "w") as file:
            file.write("\n".join(file_and_version))