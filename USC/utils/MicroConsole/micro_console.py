import os
import platform
import psutil
import sys
import shutil
import time

from multiprocessing import Process
from pyfiglet import Figlet
from colorama import Fore, Back, Style
from progress.bar import IncrementalBar
from terminaltables import AsciiTable
import keyboard

class MicroLog:
    
    def __init__(self) -> None:
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
    
    def get_log(self) -> list:
        errors = []
        warnings = []
        with open(f"{self.current_directory}/data/sessionLog.txt", "r") as log:
            lines = log.read()
            for line in lines.split("\n---\n"):
                if line != "":
                    line_type = line.split("|")[0]
                    line_message = line.split("|")[1::]
                    if line_type == "Error":
                        errors.append(line_message)
                    elif line_type == "Warning":
                        warnings.append(line_message)
                        
        return [errors, warnings]
    
    def add_warnings(self, messages:list):
        with open(f"{self.current_directory}/data/sessionLog.txt", "a") as log:
            for message in messages:
                log.write("Warning|" + message)
                log.write("\n---\n")
                
    def add_errors(self, messages:list):
        with open(f"{self.current_directory}/data/sessionLog.txt", "a") as log:
            for message in messages:
                log.write("Error|" + message)
                log.write("\n---\n")

    def clear_log(self):
        with open(f"{self.current_directory}/data/sessionLog.txt", "w") as log:
            log.write("")

class MicroConsole:
    
    def __init__(self, PackageManager, ports_config:dict, max_services:int, public_services:dict, private_services:dict) -> None:
        # init actions
        self.clear_console()
        preview_text = Figlet(font='slant')
        print(preview_text.renderText(f'MicroConsole'))
        self.log = MicroLog()
        self.log.clear_log()
        if len(ports_config.keys()) > 0:
            self.bar = IncrementalBar("Initialization", max=max_services)
        else:
            print("Initialization |████████████████████████████████| 0/0", end ="")
            
        self.ports_config = ports_config
        self.services_config = None
        self.PackageManager = PackageManager
        self.public_services = public_services
        self.private_services = private_services
        self.stdin = sys.stdin
        
    def work_cycle(self) -> None:
        time.sleep(0.5)
        log_data = self.log.get_log()
        self.errors = log_data[0]
        self.warnings = log_data[1]
        print(f"{Fore.YELLOW} | Warnings: {len(self.warnings)}  {Fore.RED}Errors: {len(self.errors)}{Fore.WHITE}")
        print(Fore.YELLOW + "Use 'help' command for get help message\n" + Fore.WHITE)
        while True:
            try:
                command = input("Enter command: ")
                if command.replace(" ", "") != "":
                    command_args = command.split(" ")
                    match command_args[0]:
                        case "exit":
                            self.close_all_services()
                            break
                        
                        # list commands
                        case "list":
                            self.show_list()
                        case "ls":
                            self.show_list()
                        # -------------
                        
                        case "log":
                            if len(command_args) != 1:
                                if command_args[1].replace(" ", "") == "*":
                                    # Create table data for errors 
                                    print(f"{Fore.RED}Errors{Fore.RESET}")
                                    table_data = [["Package", "File", "Error"]]
                                    for error in self.errors[-5::]:
                                        table_data.append([error[1], error[0], error[2]])
                                    # Creating table
                                    print(AsciiTable(table_data).table, "\n")
                                    print(f"{Fore.YELLOW}Warnings{Fore.RESET}")
                                    table_data = [["Package", "File", "Warning"]]
                                    for error in self.warnings:
                                        table_data.append([error[1], error[0], error[2]])
                                    # Creating table
                                    print(AsciiTable(table_data).table, "\n")
                                    print()
                                elif command_args[1].replace(" ", "") == "-e":
                                    table_data = [["Package", "File", "Error"]]
                                    for error in self.errors:
                                        table_data.append([error[1], error[0], error[2]])
                                    # Creating table
                                    print(AsciiTable(table_data).table, "\n")
                                elif command_args[1].replace(" ", "") == "-w":
                                    table_data = [["Package", "File", "Warning"]]
                                    for error in self.warnings:
                                        table_data.append([error[1], error[0], error[2]])
                                    # Creating table
                                    print(AsciiTable(table_data).table, "\n")
                                else:
                                    print(f"{Fore.RED}Unknown argument{Fore.RESET}")
                            else:
                                print(f"{Fore.YELLOW}Enter what log you want (-e, -w, *){Fore.RESET}")
                            
                        case "clear":
                            self.clear_console()
                            
                        case "stop":
                            self.command_template(command_args=command_args, callback=self.close_service)
                                
                        case "reboot":
                            self.command_template(command_args=command_args, callback=self.reboot_service)
                                
                        case "run":
                            self.command_template(command_args=command_args, callback=self.run_service)
                            
                        case "stats":
                            self.stats_cycle()
                            
                        case "edit":
                            if len(command_args) != 1:
                                if command_args[1].replace(" ", "") != "":
                                    package_name = ""
                                    for port in self.ports_config.keys():
                                        for package in self.ports_config[port]:
                                            if command_args[1].replace(" ", "") == package:
                                                package_name = package
                                                self.PackageManager.code(package)
                                                
                                                break
                                        else:
                                            if package_name == "":
                                                print(f"{Fore.RED}Package not found{Fore.RESET}")
                                            break
                                                
                            else:
                                print("Package not selected")
                                
                        case "help":
                            print("\n----- help message -----\n")
                            message_data = {
                                "clear" : "Clear console",
                                "stop" : "Stop service ( process )",
                                "run" : "Run service ( process )",
                                "list / ls" : "Get services info",
                                "reboot" : "Reboot service ( process )",
                                "help" : "Get help message",
                                "exit" : "Stop processes and exit from MicroConsole",
                                "edit" : "Edit package started in services (after edit need use reboot command)",
                                "stats" : "Viewing complete information about all services",
                            }
                            command_keys = list(message_data.keys())
                            command_keys.sort()
                            max_len_item = len(max(command_keys, key = len))
                            for index, key in enumerate(command_keys):
                                len_delta = max_len_item - len(key)
                                if index % 2 == 0:
                                    print(Style.BRIGHT+ Fore.BLACK + key + (" " * len_delta) + f" - {message_data[key]}" + Style.RESET_ALL + Fore.RESET)
                                else:
                                    print(Style.BRIGHT+ Fore.WHITE + key + (" " * len_delta) + f" - {message_data[key]}" + Style.RESET_ALL + Fore.RESET)

                            print()
                        
                        case _:
                            print(f"{Fore.RED}Unknown command entered{Fore.RESET}")
                            
            except KeyboardInterrupt:
                print()
            
            
        exit(0)
        
            
    def command_template(self, command_args, callback) -> None:     
        if len(command_args) != 1:
            if command_args[1].replace(" ", "") == "*":
                for service_id in self.services_config.keys():
                    callback(service_id=int(service_id))
            elif command_args[1].find(",") > 0:
                for service_id in command_args[1].split(","):
                    callback(service_id=int(service_id))
                if len(command_args) > 2:
                    print("Warning! Unknown arguments entered")
            elif command_args[1].replace(" ", "") != "":
                callback(service_id=int(command_args[1].replace(" ", "")))
        else:
            print(f"{Fore.RED}Service not selected{Fore.RESET}")
            
    def close_service(self, service_id:int) -> None:
        if self.services_config.get(service_id) != None:
            process = self.services_config[service_id]["process"]
            if process.is_alive():
                process.terminate()
                self.services_config[service_id]["active"] = process.is_alive()
        else:
            print(f"{Fore.RED}Service not found{Fore.RESET}")
        
    def reboot_service(self, service_id:int) -> None:
        if self.services_config.get(service_id) != None:
            if self.services_config[service_id]["process"].is_alive():
                self.services_config[service_id]["process"].terminate()
            # create new process
            port = self.services_config[service_id]["port"]
            if self.services_config[service_id]["status"] == "public":
                process = Process(target=self.PackageManager.run_algorithm,
                                args=(self.PackageManager.current_directory,
                                    port, self.public_services, True),
                                name=f"USCore public {port}")
            else:
                process = Process(target=self.PackageManager.run_algorithm, 
                                args=(self.PackageManager.current_directory,
                                    port,self.private_services,False),
                                name=f"USCore private {port}")
            process.start()
            # add to process config
            self.services_config[service_id]["process"] = process
            self.services_config[service_id]["active"] = process.is_alive()
        else:
            print(f"{Fore.RED}Service not found{Fore.RESET}")
        time.sleep(0.5)
        log_data = self.log.get_log()
        self.errors = log_data[0]
        self.warnings = log_data[1]
            
    def run_service(self, service_id:int) -> None:
        if self.services_config.get(service_id) != None:
            if not self.services_config[service_id]["process"].is_alive():
                # create new process
                port = self.services_config[service_id]["port"]
                if self.services_config[service_id]["status"] == "public":
                    process = Process(target=self.PackageManager.run_algorithm,
                                    args=(self.PackageManager.current_directory,
                                        port, self.public_services, True),
                                    name=f"USCore public {port}")
                else:
                    process = Process(target=self.PackageManager.run_algorithm, 
                                    args=(self.PackageManager.current_directory,
                                        port,self.private_services,False),
                                    name=f"USCore private {port}")
                process.start()
                # add to process config
                self.services_config[service_id]["process"] = process
                self.services_config[service_id]["active"] = process.is_alive()
        else:
            print(f"{Fore.RED}Service not found{Fore.RESET}")
        time.sleep(0.5)
        log_data = self.log.get_log()
        self.errors = log_data[0]
        self.warnings = log_data[1]
        
    def close_all_services(self) -> None:
        for service_id in self.services_config.keys():
            self.services_config[service_id]["process"].terminate()
            
    def clear_console(self) -> None:
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')
            
    @staticmethod
    def clear_console_lines(lines_amount):
        for _ in range(lines_amount):
            sys.stdout.write('\033[F')  # Переместить курсор вверх на одну строку
            sys.stdout.write('\033[K')
            
    def init_services_config(self, process_config:dict, public_services:dict, private_services:dict) -> None:
        new_services_config = {}
        index = 0
        for i, port in enumerate(process_config.keys()):
            for process_status in process_config[port].keys():
                new_services_config[index] = {"port": list(process_config.keys())[i], 
                                        "status": process_status,
                                        "active": process_config[list(process_config.keys())[i]][process_status].is_alive(), 
                                        "process": process_config[list(process_config.keys())[i]][process_status],
                                        "packages": self.public_services[list(process_config.keys())[i]] \
                                            if process_status == "public" \
                                            else self.private_services[list(process_config.keys())[i]]}
                index += 1
            
        self.services_config = new_services_config

    def next_init_bar(self) -> None:
        self.bar.next()
        
    def show_list(self) -> None:
        table_data = [["ID", "Active", "Port", "Packages", "Process"]]
        for service_id in range(len(self.services_config.keys())):
            table_data.append([
                service_id,
                self.services_config[service_id]["process"].is_alive(),
                self.services_config[service_id]["port"],
                ", ".join(self.services_config[service_id]["packages"]),
                self.services_config[service_id]["process"]
            ])
            
        # Creating table
        table = AsciiTable(table_data)
        print(table.table)
        
    def stats_cycle(self):
        # preparation work
        self.clear_console()
        preview_text = Figlet(font='slant')
        print(preview_text.renderText(f'MicroConsole'))
        print(f"{Fore.YELLOW}To switch between processes, press the up or down keys{Fore.RESET}")
        print(f"{Fore.RED}K{Fore.YELLOW} -> kill process | {Fore.RED}S{Fore.YELLOW} -> start process | {Fore.RED}R{Fore.YELLOW} -> reboot process{Fore.RESET}")
        print(f"{Fore.RED}F5{Fore.YELLOW} -> refresh list | {Fore.RED}Ctrl + C{Fore.YELLOW} -> exit from status menu{Fore.RESET}")
        print("\nProcess info:")
        globals()["selected_service_id"] = 0
        globals()["EXIT"] = False
        globals()["RENDER_STATE"] = False
        
        # get free lines for showing processes
        terminal_size = shutil.get_terminal_size(fallback=(80, 24))
        rows = terminal_size.lines
        max_console_lines = rows - 20 if rows > 20 else 1
        globals()["max_dysplayed_service_id"] = max_console_lines
        
        # function displaying processes
        def dysplay_services(is_more_list:bool):
            # get free lines for showing processes
            terminal_size = shutil.get_terminal_size(fallback=(80, 24))
            rows = terminal_size.lines    
            max_console_lines = rows - 20 if rows > 20 else 1
            globals()["max_dysplayed_service_id"] = max_console_lines
            # Service info in table
            table_data = [["ID", "Active", "Port", "Packages", "CPU %", "RAM ᵇᵞᵗᵉᶳ"]]
            service_port = self.services_config[globals()["selected_service_id"]]["port"]
            service_process_pid = self.services_config[globals()["selected_service_id"]]["process"].pid
            service_process_is_alive = self.services_config[globals()["selected_service_id"]]["process"].is_alive()
            table_data.append([
                globals()["selected_service_id"],
                service_process_is_alive,
                service_port,
                ", ".join(self.services_config[globals()["selected_service_id"]]["packages"]),
                "0" if not service_process_is_alive else psutil.Process(service_process_pid).cpu_percent(interval=1.0),
                "0" if not service_process_is_alive else psutil.Process(service_process_pid).memory_info().rss
            ])
            # Creating table
            print(AsciiTable(table_data).table, "\n")
            globals()["table_created"] = True
            
            # showing processes list
            print("Runned processes:")
            if not is_more_list:
                # all processes
                items_count_is_not_found =  globals()["max_dysplayed_service_id"] - len(self.services_config.keys())
                for service_id in self.services_config.keys():
                    item = self.services_config[service_id]
                    if globals()["selected_service_id"] == service_id:
                        print(f"\t{Back.WHITE}{Fore.BLACK}{service_id} - {item["process"]}{Fore.RESET}{Back.RESET}")
                    else:
                        print(f"\t{service_id} - {item["process"]}")
                
                for i in range(items_count_is_not_found):
                    print(f"\tEmpty - <Empty>")
            else:
                # Choiced processe
                items_count_is_not_found = globals()["max_dysplayed_service_id"] - (len(list(self.services_config.keys())[globals()["selected_service_id"]:globals()["selected_service_id"] + globals()["max_dysplayed_service_id"]]))
                for service_id in list(self.services_config.keys())[globals()["selected_service_id"]:globals()["selected_service_id"] + globals()["max_dysplayed_service_id"]]:
                    item = self.services_config[service_id]
                    if globals()["selected_service_id"] == service_id:
                        print(f"\t{Back.WHITE}{Fore.BLACK}{service_id} - {item["process"]}{Fore.RESET}{Back.RESET}")
                    else:
                        print(f"\t{service_id} - {item["process"]}")
                
                for i in range(items_count_is_not_found):
                    print(f"\tEmpty - <Empty>")
                
        def controll_cycle():
            # cycle for use keyboard and restart console rendering
            old_max_dysplaed_service_id = globals()["max_dysplayed_service_id"]
            while True:
                try:
                    # get free lines for showing processes
                    terminal_size = shutil.get_terminal_size(fallback=(80, 24))
                    rows = terminal_size.lines      
                    max_console_lines = rows - 20 if rows > 20 else 1
                    globals()["max_dysplayed_service_id"] = max_console_lines 
                    if globals()["max_dysplayed_service_id"] != old_max_dysplaed_service_id:
                        break
                    
                    # Keyboard controll
                    def rerender_console():
                        if globals()["table_created"]:
                                self.clear_console_lines( globals()["max_dysplayed_service_id"] + 7)
                        else:
                            self.clear_console_lines( globals()["max_dysplayed_service_id"])
                        dysplay_services(is_more_list=globals()["RENDER_STATE"])
                    
                    def up_process():
                        if 0 < globals()["selected_service_id"]:
                            globals()["selected_service_id"] -= 1
                            rerender_console()
                        
                    def down_process():
                        if len(self.services_config.keys()) - 1 > globals()["selected_service_id"]:
                            globals()["selected_service_id"] += 1
                            rerender_console()
                        
                    if keyboard.is_pressed('Up'):
                        up_process()
                    if keyboard.is_pressed('Down'):
                        down_process()
                    if keyboard.is_pressed('K'):
                        self.close_service(service_id=globals()["selected_service_id"])
                        rerender_console()
                    if keyboard.is_pressed('S'):
                        self.run_service(service_id=globals()["selected_service_id"])
                        rerender_console()
                    if keyboard.is_pressed('R'):
                        self.reboot_service(service_id=globals()["selected_service_id"])
                        rerender_console()
                    if keyboard.is_pressed('F5'):
                        rerender_console()    


                except KeyboardInterrupt:
                    globals()["EXIT"] = True
                    break
                
            if not globals()["EXIT"]:  
                if globals()["max_dysplayed_service_id"] != old_max_dysplaed_service_id:
                    old_max_dysplaed_service_id = globals()["max_dysplayed_service_id"]
                    # restart console preparation work
                    self.clear_console()
                    preview_text = Figlet(font='slant')
                    print(preview_text.renderText(f'MicroConsole'))
                    print(f"{Fore.YELLOW}To switch between processes, press the up or down keys{Fore.RESET}")
                    print(f"{Fore.RED}K{Fore.YELLOW} -> kill process | {Fore.RED}S{Fore.YELLOW} -> start process | {Fore.RED}R{Fore.YELLOW} -> reboot process{Fore.RESET}")
                    print(f"{Fore.RED}F5{Fore.YELLOW} -> refresh list | {Fore.RED}Ctrl + C{Fore.YELLOW} -> exit from status menu{Fore.RESET}")
                    print("\nProcess info:")
                    if len(self.services_config.keys()) > max_console_lines - 1:
                        globals()["RENDER_STATE"] = True
                        dysplay_services(is_more_list=globals()["RENDER_STATE"])
                    else:
                        globals()["RENDER_STATE"] = False
                        dysplay_services(is_more_list=globals()["RENDER_STATE"])
                    controll_cycle() 
            
        # main cycle
        # show services
        globals()["table_created"] = False
        if len(self.services_config.keys()) > max_console_lines - 1:
            globals()["RENDER_STATE"] = True
            dysplay_services(is_more_list=globals()["RENDER_STATE"])
            controll_cycle()
        else:
            globals()["RENDER_STATE"] = False
            dysplay_services(is_more_list=globals()["RENDER_STATE"])
            controll_cycle()