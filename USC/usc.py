""" main starting file """

import sys
import configparser

from pyfiglet import Figlet

from __package_manager import PackageManager

sys_args = sys.argv[1::]
Manager = PackageManager()
config = configparser.ConfigParser()

preview_text = Figlet(font='slant')
hello_message = preview_text.renderText('USC')


# Get server config
# config.read('run.ini')
# server_config = config['SERVER']

if len(sys.argv) > 1:
    match sys_args[0]:
        
        case "install":
            Manager.install(name=sys_args[1])
                
        case "uninstall":
            Manager.uninstall(name=sys_args[1])
        
        case "refresh":
            Manager.refresh()
        
        case "create":
            Manager.create(name=sys_args[1])
        
        case "list":
            print(Manager.get_list())
        
        case "update":
            pass
        
        case "upgrade":
            pass
        
        case "run":
            pass
        
        case "server":
            Manager.set_server_config(server_info=sys_args[1], is_my_server=False)

        case "config":
            Manager.set_server_config(server_info=sys_args[1], is_my_server=True)
        
        case "-h":
            pass
        
        case "-v":
            preview_text = Figlet(font='larry3d')
            print(preview_text.renderText('------'))
            print(preview_text.renderText('V-0.0.1'))
            print(preview_text.renderText('------'))
            

        case _:
            print("Unknown command")
else:
    print(hello_message)