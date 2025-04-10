import os

def clean_path(path_str:str):
    if path_str.endswith(('\\','/')):
        return clean_path(path_str[0:-1])
    path_str = path_str.replace('/', os.sep).replace('\\', os.sep)
    return path_str.strip(" \'\n\"\u202a")#path_str.strip(" ").strip('\'').strip("\n").strip('"').strip(" ").strip("\u202a")