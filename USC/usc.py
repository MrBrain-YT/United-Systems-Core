""" main starting file """

import sys
import configparser
import os
import re

import requests
from pyfiglet import Figlet

from __package_manager import PackageManager


Manager = PackageManager()
config = configparser.ConfigParser()

preview_text = Figlet(font='slant')
hello_message = preview_text.renderText('USC')


# Get server config
# config.read('run.ini')
# server_config = config['SERVER']

sys_args = sys.argv[1::]

if len(sys.argv) > 1:
    match sys_args[0]:
        
        case "install":
            github_url_pattern = r'^https?://github\.com/.+/.+\.git$'
            if not re.match(github_url_pattern, sys_args[1]):
                Manager.install(name=sys_args[1])
            else:
                Manager.install_git(url=sys_args[1])
                
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
            # version = requests.get("https://raw.githubusercontent.com/MrBrain-YT/United-Systems-Core/Development/version")
            # if version.status_code == 200:
            #     preview_text = Figlet(font='larry3d')
            #     print(preview_text.renderText('------'))
            #     print(preview_text.renderText(f'V-{version.text}'))
            #     print(preview_text.renderText('------'))
            # else:
            pass
        
        case "run":
            pass
        
        case "export":
            Manager.export(name=sys_args[1])
        
        case "server":
            Manager.set_server_config(server_info=sys_args[1], is_my_server=False)

        case "config":
            Manager.set_server_config(server_info=sys_args[1], is_my_server=True)
        
        case "-h":
            pass
        
        case "-v":
            with open(f'{os.path.dirname(os.path.abspath(__file__))}/version', "r") as ver:
                version = ver.read()
            preview_text = Figlet(font='larry3d')
            print(preview_text.renderText('------'))
            print(preview_text.renderText(f'V-{version}'))
            print(preview_text.renderText('------'))
            
        case _:
            print("Unknown command")
else:
    print(hello_message)
    print("To find out more use '-h'")