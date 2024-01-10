""" main starting file """

import sys
import configparser
import os
import re
import pprint

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
            github_url_pattern = r'^https?://github\.com/.+/.+\.git$'
            for package in sys_args[1].split(","):
                if not re.match(github_url_pattern, package):
                    Manager.install(name=package)
                else:
                    Manager.install_git(url=package)
                
        case "remove":
            Manager.remove(names=sys_args[1].split(","))
        
        case "refresh":
            Manager.refresh()
        
        case "create":
            Manager.create(names=sys_args[1].split(","))
        
        case "list":
            print(Manager.get_list())
        
        case "update":
            Manager.update()
        
        case "run":
            if len(sys_args) == 1:
                Manager.run()
            else:
                if len(sys_args) > 2:
                    print("Warning - unknown arguments passed")
                Manager.run(package=sys_args[1])
        
        case "export":
            Manager.export(names=sys_args[1].split(","))
            
        case "code":
            if len(sys_args) == 1:
                Manager.code(name="", no_package=True)
            elif len(sys_args) == 2:
                Manager.code(name=sys_args[1])
            elif len(sys_args) == 3:
                Manager.code(name=sys_args[1], ide=sys_args[2])
            elif len(sys_args) > 3:
                Manager.code(name=sys_args[1], ide=sys_args[2])
                print("Warning - unknown arguments passed")
                
        case "templates":
            Manager.templates()
            
        case "static":
            Manager.static()
                
        case "server":
            Manager.set_server_config(server_info=sys_args[1], is_my_server=False)

        case "config":
            Manager.set_server_config(server_info=sys_args[1], is_my_server=True)
        
        case "-h":
            print(hello_message)
            pprint.pprint(Manager.help_message())
            print()
        
        case "-v":
            Manager.core_version()
            
        case _:
            print("Unknown command")
else:
    print(hello_message)
    print("To find out more use '-h'")