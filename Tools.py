# Tools.py
import os

def read_data_from_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()

def list_data_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.dat')]

def read_data_from_server(server_id):
    directory = f'data/ES{server_id}'
    if not os.path.exists(directory):
        return {}
    data_files = list_data_files(directory)
    data = {}
    for file in data_files:
        file_path = os.path.join(directory, file)
        data[file] = read_data_from_file(file_path)
    return data