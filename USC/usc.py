""" main starting file """

import sys

from __package_manager import PackageManager

sys_args = sys.argv[1::]
Manager = PackageManager()


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
        pass
    
    case "-h":
        pass
    
    case "-v":
        print("Current United Systems Core version: 0.0.1")

    case _:
        print("Unknown command")
            
