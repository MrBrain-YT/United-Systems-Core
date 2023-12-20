import re

class ListWorker():

    def __init__(self, path:str) -> None:
        self.__path = path

    def add_package_to_list(self, name:str, version:str) -> None:
        with open(self.__path, "r") as file:
            text = file.read()
        if text != "":     
            with open(self.__path, "a") as file:
                file.write("\n" + name + f"=={version}")
        else:
            with open(self.__path, "a") as file:
                file.write(name + f"=={version}")

    def remove_package_from_list(self, name:str) -> None:
        with open(self.__path, "r") as file:
            text = file.readlines()
            lines = []
            for line in text:
                if line == "\n":
                    continue
                elif re.search(name+r"==\d.\d.\d", string=line):
                    continue
                else:
                    lines.append(line)
            with open(self.__path, "w") as file:
                file.write("".join(lines))