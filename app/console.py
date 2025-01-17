from datetime import datetime
import os
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.prompt import Prompt
from rich.spinner import Spinner
from app.console_utils import ConsoleConfig
from app.llm.llm import LLM
from app.llm.llm_utils import ollama_serve
from typing import Union
from collections.abc import Callable
from app.utils import load_spreadsheet
import requests
import sys
import webbrowser
import subprocess
from app.models import validate_dataframe, bulk_short_synopsis_schema
from threading import Thread
from http.server import HTTPServer, SimpleHTTPRequestHandler

cns_cfg = ConsoleConfig()
cns = Console()
error_console = Console(stderr=True, style="bold red")
pmt = Prompt()

class LLMConsole():
    def __init__(self):
        self.main_menu_choices = ['short synopsis', 'long synopsis']
    def prompt_loop(self, prompt:str, choices:Union[list, dict]=None, defualt=""):
        if not choices:
            response = pmt.ask(prompt=prompt, console=cns, default=defualt)
            if response == "":
                cns.print(cns_cfg.no_response_error)
                return self.prompt_loop(prompt)
            else:
                return response
        elif isinstance(choices, list):
            choice_dict = {}
            for choice in choices:
                method_name = choice.replace(' ', '_').lower()
                if hasattr(self, method_name):
                    choice_dict[choice] = getattr(self, method_name)
            choices = choice_dict
        choice_list = [k for k, v in choices.items()]
        response = pmt.ask(prompt=prompt, console=cns, choices=choice_list)
        if response.lower() not in choice_list:
            cns.print(cns_cfg.general_error)
            return self.prompt_loop(prompt,  choices=choices)
        elif response.lower() == "x" or response.lower() == "quit":
            self.quit()
        elif response.lower() == "h" or response.lower() == "help":
            self.help()
        elif response.lower() == "m" or response.lower() == "main menu":
            self.main_menu()
        else:
            c = choices[response.lower()]
            if isinstance(c, Callable):
                return c()
            elif isinstance(c, str):
                return c
    def help(self):
        cns.log("[green]Opening help guide in a browser window")

        # Start a local HTTP server
        def start_server():
            os.chdir("app/usage")  # Change to the directory containing help files
            httpd = HTTPServer(("localhost", 8000), SimpleHTTPRequestHandler)
            httpd.serve_forever()

        # Start the server in a separate thread
        server_thread = Thread(target=start_server, daemon=True)
        server_thread.start()

        # Open the help guide in the browser
        webbrowser.open("http://localhost:8000/usage_guide.html")
    def quit(self):
        cns.print('[red]Exiting...[/]')
        sys.exit(0)
    def main_menu(self):
        cns.print(cns_cfg.main_menu)
        choice_menu, chocie_dict = self.generate_menu(self.main_menu_choices)
        response = self.prompt_loop(choice_menu, choices=chocie_dict)
        if isinstance(response, str):
            method_name = response.replace(' ', '_').lower()
            if hasattr(self, method_name):
                return getattr(self, method_name)()
        else:
            return self.main_menu()
    def bulk_import(self):
        filepath = self.prompt_loop("Enter the path to your csv or xlsx file")
        df = load_spreadsheet(filepath)
        if validate_dataframe(df, bulk_short_synopsis_schema):
            return df, Path(filepath)
        
        
    def generate_menu(self, choices):
        choice_menu = ["Which would you like?:\n"]
        choice_dict = {}
        for i, choice in enumerate(choices):
            choice_number = str(i+1)
            choice_menu.append(f"{choice_number}) {choice}")
            choice_dict[choice_number] = choice
        choice_dict['m'] = 'main menu'
        choice_dict['h'] = 'help'
        choice_dict['x'] = 'quit'
        return "\n".join(choice_menu), choice_dict
    def load_ollama(self):
            if ollama_serve():
                cns.log('AI Engine loaded successfully')
                return True
            else:
                error_console.log("""ERROR: It looks like the Ollama program is not running on your computer.\nAn attempt was made to open it, but was unsuccessfull.\n
                                    Likely, Ollama is either not on your computer, or not in your system's PATH enviroment variable. Please exit and open Ollama.""")
                self.quit()
    def short_synopsis(self):
        with cns.status("Loading AI, please wait...", spinner="dots7"):
            self.load_ollama()
            llm = LLM()
        choices = ['shorten a synopsis', 'bulk shorten synopsis']
        choice_menu, chocie_dict = self.generate_menu(choices)
        response = self.prompt_loop(f"""
                        [b]Short Synopsis Generator[/]
                        [i]Shortens a Synopsis to any character length[/]
                        {choice_menu}""", chocie_dict
                        )
        def _short_synopsis(synopsis, context, max_length):
            max_character_length = int(max_length)
            with cns.status("Generating a shortened synopsis, please wait", spinner="aesthetic"):
                res, pass_count = llm.generate_with_qc_pass(synopsis, context, max_length=max_character_length)
            cns.log(res)
            char_count = len(res)
            char_count_str = str(char_count)
            if char_count <= max_character_length and char_count >= int(round(max_character_length/2,0)):
                char_count_color = "green"
                msg = f"[green]The character count is [i]{char_count_str}[/i], near to your max character limit.[/green]"
            elif char_count <= int(round(max_character_length/2,0)):
                char_count_color = "yellow"
                msg = f"[yellow]The character count is [i]{char_count_str}[/i], quite a bit lower than your max character limit.[/yellow]"
            elif char_count > max_character_length:
                char_count_color = "red"
                msg = f"[red]The character count is [i]{char_count_str}[/i], over your max character limit.[/red]"
            cns.log(f"Character Count: [{char_count_color}]{char_count_str}[/]")
            cns.log(msg)
            return res
        def _max_char_length():
            max_character_length = self.prompt_loop(" Max Character length [i]Optional[/]", defualt="80")
            try:
                max_character_length = int(max_character_length)
                return max_character_length
            except:
                cns.log("That's not an integer! try again.")
                return _max_char_length()
        if response ==  'shorten a synopsis':
            synopsis = self.prompt_loop("Your synopsis [i]Required[/]")
            max_character_length = _max_char_length()
            context = self.prompt_loop("Additional Context (Name of the episode's show, genre, keywords, etc) [i]Optional[/]", defualt="None")
            _short_synopsis(synopsis, context, max_character_length)
        elif response == 'bulk shorten synopsis':
            df, filepath = self.bulk_import()
            ext = filepath.suffix
            filename = filepath.name.replace(ext, "")
            par = filepath.parent
            export_path = os.path.join(filepath.parent, filepath.name + "_" + datetime.now().strftime("%Y-%m-%d_%H_%M_%S") + ext)
            df['short_synopsis'] = ''
            max_character_length = _max_char_length()
            context_list = ["title", "genre", "keywords","show_synopsis"]
            for index, row in df.iterrows():
                context = ", ".join([f"{k}:{v}" for k, v in row.items() if k in context_list])
                short_synopsis_value = _short_synopsis(row['synopsis'], context, max_character_length)
                df.loc[index, 'short_synopsis'] = short_synopsis_value  # Update the DataFrame directly
            if ext == ".csv":
                df.to_csv(export_path, encoding="utf-8", index=False)
            elif ext == ".xlsx":
                df.to_excel(export_path, index=False)
            cns.log(f"[green]Exported to {export_path}")
        self.main_menu()
    def long_synopsis(self):
        pass