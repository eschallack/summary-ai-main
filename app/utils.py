# utilities for loading files
import yaml
from pathlib import Path
import pandas as pd
from typing import Union

def load_spreadsheet(file_path:str) -> Union[pd.DataFrame,None]:
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    ext = _absolute_path.suffix
    if ext == ".csv":
        return pd.read_csv(_absolute_path, encoding="utf-8")
    elif ext == ".xlsx":
        return pd.read_excel(_absolute_path)
    else:
        print("Failed to load unknown File Extension")
        return None

def open_file(filepath:str):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def load_local_yaml(file_path:str):
    _here = Path(__file__).parent
    _absolute_path = (_here / '..' / file_path).resolve()
    return yaml.safe_load(open_file(_absolute_path))

if __name__ == '__main__':
    load_spreadsheet(r"C:\Users\eschallack\Documents\GitHub\short-synopsis-ai\short_synopsis_ai.py")
