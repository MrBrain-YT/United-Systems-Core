""" main starting file """

import sys
import configparser

from __package_manager import PackageManager

sys_args = sys.argv[1::]
Manager = PackageManager()
config = configparser.ConfigParser()

# Get server config
config.read('run.ini')
server_config = config['SERVER']


match sys_args[0]:
    
    case "install":
        Manager.install(name=sys_args[1])
            
    case "uninstall":
        Manager.uninstall(name=sys_args[1])
    
    case "refresh":
        pass
    
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
        print("Current United Systems Core version: 0.0.1")

    case _:
        print("Unknown command")
            
