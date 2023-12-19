import os
import time

from __list_work import ListWorker
from progress.bar import ShadyBar

class PackageManager():
    
    def __init__(self) -> None:
        self.list = ListWorker(path="__packages")
    
    def install(self, name:str) -> None:
        self.create(name=name)
        name = name.lower()
        with ShadyBar('Installing', max=20) as bar:
            for i in range(20):
                time.sleep(0.5)
                bar.next()
                   
        with open(f"packages/{name}/{name}.pkg", "w") as file:
            file.write("package installed")
            
    def uninstall(self, name:str) -> None:
        self.list.remove_package_from_list(name=name)
        os.rmdir(f"packages/{name}")
        
    def create(self, name:str) -> None:
        self.list.add_package_to_list(name=name)
        os.makedirs(f"packages/{name}")

    def get_list(self) -> str:
        with open("__packages", "r") as file:
            text = file.read()
        return text 