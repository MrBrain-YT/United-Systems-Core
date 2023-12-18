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
    
    case "refrash":
        pass
    
    case "create":
        pass
    
    case "list":
        pass
    
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