""" main starting file """

import sys
import configparser
import re
import pprint

from colorama import Fore
from pyfiglet import Figlet

from __package_manager import PackageManager


Manager = PackageManager()
config = configparser.ConfigParser()

preview_text = Figlet(font='slant')
hello_message = preview_text.renderText('USC')


sys_args = sys.argv[1::]

if len(sys.argv) > 1:
    match sys_args[0]:
        
        case "install":
            if len(sys_args) > 1:
                github_url_pattern = r'^https?://github\.com/.+/.+\.git$'
                for package in sys_args[1].split(","):
                    if not re.match(github_url_pattern, package):
                        Manager.install(name=package)
                    else:
                        Manager.install_git(url=package)
            else:
                print(Fore.RED + "Please enter package name for install package")
                    
        case "import":
            if len(sys_args) > 1:
                Manager.import_package(paths=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter path to tar.gz file for import package")
                
        case "remove":
            if len(sys_args) > 1:
                Manager.remove(names=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter package name for remove package")
        
        case "refresh":
            Manager.refresh()
            if len(sys_args) > 1:
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
        
        case "create":
            if len(sys_args) > 1:
                Manager.create(names=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter package name for create package")
        
        case "list":
            print(Manager.get_list())
            if len(sys_args) > 1:
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
        
        case "update":
            Manager.update()
            if len(sys_args) > 1:
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
        
        case "run":
            if len(sys_args) == 1:
                Manager.run()
            else:
                if len(sys_args) > 2:
                    print(Fore.YELLOW + "Warning! Unknown arguments entered")
                Manager.run(package=sys_args[1])
        
        case "export":
            if len(sys_args) > 1:
                Manager.export(names=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter package name for export package")
            
        case "code":
            if len(sys_args) == 1:
                Manager.code(name="", no_package=True)
            elif len(sys_args) == 2:
                Manager.code(name=sys_args[1])
            elif len(sys_args) == 3:
                Manager.code(name=sys_args[1], ide=sys_args[2])
            elif len(sys_args) > 3:
                Manager.code(name=sys_args[1], ide=sys_args[2])
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
                
        case "templates":
            if len(sys_args) == 2:
                Manager.templates(package=sys_args[1])
            elif len(sys_args) > 2:
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
            else:
                Manager.templates()
            
        case "static":
            if len(sys_args) == 2:
                Manager.static(package=sys_args[1])
            elif len(sys_args) > 2:
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
            else:
                Manager.static()
                
        case "server":
            if len(sys_args) == 2:
                Manager.set_server_config(server_info=sys_args[1], is_my_server=False)
            elif len(sys_args) > 2:
                Manager.set_server_config(server_info=sys_args[1], is_my_server=False)
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
            else:
                print(Fore.RED + "Please enter ip and port")

        case "config":
            if len(sys_args) == 2:
                Manager.set_server_config(server_info=sys_args[1], is_my_server=True)
            elif len(sys_args) > 2:
                Manager.set_server_config(server_info=sys_args[1], is_my_server=True)
                print(Fore.YELLOW + "Warning! Unknown arguments entered")
            else:
                print(Fore.RED + "Please enter ip and port")
        
        case "-h":
            print(hello_message)
            pprint.pprint(Manager.help_message())
            print()
            if len(sys_args) > 1:
                print(Fore.RED + "Warning! Unknown arguments entered")
        
        case "-v":
            Manager.core_version()
            if len(sys_args) > 1:
                print(Fore.RED + "Warning! Unknown arguments entered")
            
        case _:
            print("Unknown command")
else:
    print(hello_message)
    print(Fore.YELLOW + "To find out more use '-h'")