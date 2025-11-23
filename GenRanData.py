import os
import random
import shutil
from Config import data_scale, data_size, es_scale, corrupted_edge_ratio, corrupted_data_ratio

def clean_directories(base_path='data', silent=False):
    """
    Deletes all existing files and directories under the base path.
    """
    if os.path.exists(base_path):
        shutil.rmtree(base_path)
    
    if not silent:
        print(f"[Init] Cleaned data directory '{base_path}'.")

def create_directories(silent=False):
    """
    Generates data, distributes it, and introduces corruption.
    Set silent=True to suppress console output during batch experiments.
    """
    os.makedirs('data', exist_ok=True)
    os.makedirs('data/AppVend', exist_ok=True)
    for i in range(1, es_scale + 1):
        os.makedirs(f'data/ES{i}', exist_ok=True)

    # 1. Generate AppVend Data (Ground Truth)
    if not silent:
        print(f"[Init] Generating {data_scale} AppVend files...")
    
    for i in range(1, data_scale + 1):
        filename = f'd_{i}.dat'
        # Generate random binary data
        data = os.urandom(data_size)
        with open(f'data/AppVend/{filename}', 'wb') as f:
            f.write(data)

    # 2. Distribute Data to Edge Servers (Partial Coverage)
    record_table = {}
    all_files = [f'd_{i}.dat' for i in range(1, data_scale + 1)]
    
    for es_id in range(1, es_scale + 1):
        # Determine subset size (randomly between 40% and 70% of total data)
        subset_size = random.randint(int(data_scale * 0.4), int(data_scale * 0.7))
        subset_size = max(1, subset_size)
        
        assigned_files = random.sample(all_files, subset_size)
        record_table[es_id] = assigned_files
        
        for file_name in assigned_files:
            src = f'data/AppVend/{file_name}'
            dst = f'data/ES{es_id}/{file_name}'
            shutil.copyfile(src, dst)

    # 3. Introduce Corruption
    # Determine how many servers are corrupted
    num_corrupted_servers = int(corrupted_edge_ratio * es_scale)
    # Randomly select which servers are corrupt
    corrupted_server_ids = random.sample(range(1, es_scale + 1), num_corrupted_servers)
    
    if not silent:
        print("\n" + "="*40)
        print(f"!!! GROUND TRUTH: CORRUPTED SERVERS: {corrupted_server_ids} !!!")
        print("="*40 + "\n")
    
    for es_id in corrupted_server_ids:
        files = record_table[es_id]
        if not files: continue
        
        # Determine how many files on this server are corrupt
        num_corrupted_files = max(1, int(corrupted_data_ratio * len(files)))
        files_to_corrupt = random.sample(files, num_corrupted_files)
        
        for file_name in files_to_corrupt:
            file_path = f'data/ES{es_id}/{file_name}'
            # Overwrite with random garbage
            with open(file_path, 'wb') as f:
                f.write(os.urandom(data_size))
            
            if not silent:
                print(f"  -> Corrupted {file_name} on Server {es_id}")

    return record_table

if __name__ == "__main__":
    # If run directly, be verbose
    clean_directories()
    create_directories(silent=False)