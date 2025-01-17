# utilities for loading and validating prompts and responses.

from pathlib import Path
import yaml
from collections.abc import Callable
import json
from app.utils import load_local_yaml
from typing import List, Dict
import requests
from subprocess import Popen, PIPE


def load_local_yaml_prompt(file_path:str):
    json_template = load_local_yaml(file_path)
    return json_template['chat_prompt'], json_template['system_prompt']

def create_context(data:Dict[str,str]):
    output = []
    for k, v in data.items():
        output.append(f"{k}: {v}")
    return "\n".join(output)
        
def ollama_serve():
    r = requests.get("http://localhost:11434")
    if r.status_code != 200:
        p = Popen(['ollama', 'serve'], stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0: 
            print("Ollama Failed To Start %d %s %s" % (p.returncode, output, error))
            return False
        else:
            return True
    else:
        return True