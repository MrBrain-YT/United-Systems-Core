import os
import time

from progress.bar import Bar

class PackageManager():
    
    def __init__(self) -> None:
        pass
    
    def install(self, name:str) -> None:
        name = name.lower()
        with Bar('Processing', max=20) as bar:
            for i in range(20):
                time.sleep(0.5)
                bar.next()
                   
        with open(f"packages/{name}.pkg", "w") as file:
            file.write("package installed")
            
    def uninstall(self, name:str) -> None:
        os.remove(f"packages/{name.lower()}.pkg")