""" main starting file """

import sys
import configparser
import re

from colorama import Fore, Style
from pyfiglet import Figlet

from utils.package_manager import PackageManager


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
                Manager.refresh()
            else:
                print(Fore.RED + "Please enter package name for install package" + Fore.RESET)
                    
        case "import":
            if len(sys_args) > 1:
                Manager.import_package(paths=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter path to tar.gz file for import package" + Fore.RESET)
                
        case "remove":
            if len(sys_args) > 1:
                Manager.remove(names=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter package name for remove package" + Fore.RESET)
        
        case "refresh":
            Manager.refresh()
            if len(sys_args) > 1:
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
                
        case "python":
            print(sys_args[1::])
            if len(sys_args[1::]) > 0:
                Manager.python_run(py_args=" ".join(sys_args[1::]))
                # Manager.python_run(py_args="")
            else:
                Manager.python_run(py_args="")

        case "create":
            if len(sys_args) > 1:
                Manager.create(names=sys_args[1].split(","))
            else:
                print(Fore.RED + "Please enter package name for create package" + Fore.RESET)
        
        case "list":
            print(Manager.get_list())
            if len(sys_args) > 1:
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
        
        case "update":
            Manager.update()
            if len(sys_args) > 1:
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
        
        case "run":
            if __name__ == '__main__': 
                if len(sys_args) > 3:
                    print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
                    
                if len(sys_args) == 1:
                    Manager.run()
                    
                elif len(sys_args) == 2:
                    if sys_args[1] == "ignore":
                        Manager.run(ignore=True)
                    else:
                        Manager.run(line_packages=sys_args[1], ignore=False)
                        
                elif len(sys_args) == 3:
                    if sys_args[2] == "ignore":
                        Manager.run(line_packages=sys_args[1], ignore=True)
                    elif sys_args[1] == "ignore":
                        Manager.run(line_packages=sys_args[2], ignore=True)
        
        case "export":
            if len(sys_args) == 2:
                Manager.export(names=sys_args[1].split(","))
            elif len(sys_args) == 3:
                Manager.export(names=sys_args[1].split(","), path=sys_args[2])
            elif len(sys_args) > 3:
                Manager.export(names=sys_args[1].split(","), path=sys_args[2])
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
            else:
                print(Fore.RED + "Please enter package name for export package" + Fore.RESET)
            
        case "code":
            if len(sys_args) == 1:
                Manager.code(name="", no_package=True)
            elif len(sys_args) == 2:
                Manager.code(name=sys_args[1])
            elif len(sys_args) == 3:
                Manager.code(name=sys_args[1], ide=sys_args[2])
            elif len(sys_args) > 3:
                Manager.code(name=sys_args[1], ide=sys_args[2])
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
                
        case "templates":
            if len(sys_args) == 2:
                Manager.templates(package=sys_args[1])
            elif len(sys_args) > 2:
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
            else:
                Manager.templates()
            
        case "static":
            if len(sys_args) == 2:
                Manager.static(package=sys_args[1])
            elif len(sys_args) > 2:
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
            else:
                Manager.static()
                
        case "server":
            if len(sys_args) == 1:
                Manager.set_server_config(read=True, server_info=sys_args[0], is_my_server=False)
            elif len(sys_args) == 2:
                Manager.set_server_config(read=False, server_info=sys_args[1], is_my_server=False)
            elif len(sys_args) > 2:
                Manager.set_server_config(read=False, server_info=sys_args[1], is_my_server=False)
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)

        case "config":
            if len(sys_args) == 1:
                Manager.set_server_config(read=True, server_info=sys_args[0], is_my_server=True)
            elif len(sys_args) == 2:
                Manager.set_server_config(read=False, server_info=sys_args[1], is_my_server=True)
            elif len(sys_args) > 2:
                Manager.set_server_config(read=False, server_info=sys_args[1], is_my_server=True)
                print(Fore.YELLOW + "Warning! Unknown arguments entered" + Fore.RESET)
        
        case "-h":
            print(hello_message)
            command_keys = list(Manager.help_message().keys())
            command_keys.sort()
            max_len_item = len(max(command_keys, key = len))
            for index, key in enumerate(command_keys):
                len_delta = max_len_item - len(key)
                if index % 2 == 0:
                    print(Style.BRIGHT+ Fore.BLACK + key + (" " * len_delta) + f" - {Manager.help_message()[key]}" + Style.RESET_ALL + Fore.RESET)
                else:
                    print(Style.BRIGHT+ Fore.WHITE + key + (" " * len_delta) + f" - {Manager.help_message()[key]}" + Style.RESET_ALL + Fore.RESET)
            print()
            
            if len(sys_args) > 1:
                print(Fore.RED + "Warning! Unknown arguments entered" + Fore.RESET)
        
        case "-v":
            Manager.core_version()
            if len(sys_args) > 1:
                print(Fore.RED + "Warning! Unknown arguments entered" + Fore.RESET)
            
        case _:
            print("Unknown command" + Fore.RESET)
else:
    print(hello_message)
    print(Fore.YELLOW + "To find out more use '-h'" + Fore.RESET)