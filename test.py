import os

def get_json_file_path(directory_path, recursive=False):
    # 校验路径有效性
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"提供的路径 '{directory_path}' 不存在或不是文件夹")
    
    # 定义不同遍历模式的文件收集方式
    def scan_files():
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.json'):
                        yield os.path.join(root, file)
        else:
            for file in os.listdir(directory_path):
                full_path = os.path.join(directory_path, file)
                if os.path.isfile(full_path) and file.endswith('.json'):
                    yield full_path
    
    # 执行扫描并返回排序结果
    return sorted(scan_files(), key=lambda x: (not os.path.basename(x).startswith('config'), x))
print(get_json_file_path(r'D:\ODCmonitor\monitorODC\ODCelement')[0])