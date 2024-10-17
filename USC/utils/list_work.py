import os
import configparser

class ListWorker():

    def __init__(self) -> None:
        pass
        
        
    def check_exits(self, name:str) -> bool:
        dir_path = f"{os.path.dirname(os.path.abspath(__file__))}/packages"
        config = configparser.ConfigParser()
        config.read(f"{dir_path}/packages.ini")
        if name.lower() in config.sections():
            return True
        else:
            return False

    def add_package_to_list(self, package_config:configparser.ConfigParser) -> None:
        dir_path = f"{os.path.dirname(os.path.abspath(__file__))}/packages"
        package_name = package_config["INFO"].get("name")
        package_version = package_config["INFO"].get("version")
        package_os = package_config["INFO"].get("os")
        
        # Backward compatibility
        imported_package_config = configparser.ConfigParser()
        imported_package_config.read(f"{dir_path}/{package_name.lower()}/package.ini")
        ## (port)
        if package_config["INFO"].get("port") is not None:
            package_port = package_config["INFO"].get("port")
        else:
            imported_package_config["INFO"]["port"] = '5000'
            package_port = "5000"
            with open(f"{dir_path}/{package_name.lower()}/package.ini", 'w') as configfile:
                imported_package_config.write(configfile)
        ## (status)
        if package_config["INFO"].get("status") is not None:
            package_status = package_config["INFO"].get("status")
        else:
            imported_package_config["INFO"]["status"] = 'private'
            package_status = "private"
            with open(f"{dir_path}/{package_name.lower()}/package.ini", 'w') as configfile:
                imported_package_config.write(configfile)
                
        
        # Add package to package list
        config = configparser.ConfigParser()
        config.read(f"{dir_path}/packages.ini")
        if package_name not in config.sections():
            config[package_name.lower()] = {
                "name" : package_name,
                "version" :package_version,
                "os" : package_os.lower(),
                "port" : package_port,
                "status" : package_status
            }
            with open(f"{dir_path}/packages.ini", 'w') as configfile:
                config.write(configfile)

    def remove_package_from_list(self, name:str) -> None:
        dir_path = f"{os.path.dirname(os.path.abspath(__file__))}/packages"
        config = configparser.ConfigParser()
        config.read(f"{dir_path}/packages.ini")
        if config.has_section(name):
            config.remove_section(name)
        
        with open(f"{dir_path}/packages.ini", 'w') as configfile:
            config.write(configfile)