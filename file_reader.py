import pandas as pd

def load_file(file_path):
    """
    Generalized data loader.
    Supports: CSV, Excel, and JSON files.
    Handles multiple common encodings automatically.
    """
    file_extension = file_path.lower().split('.')[-1]

    try:
        if file_extension in ['xlsx', 'xls']:
            return pd.read_excel(file_path)
        if file_extension == 'json':
            return pd.read_json(file_path)
        if file_extension == 'csv':
            for encoding, sep in [('utf-8', ','), ('utf-16', '\t'), ('latin1', ',')]:
                try:
                    return pd.read_csv(file_path, encoding=encoding, sep=sep)
                except UnicodeDecodeError:
                    continue
        raise ValueError(f"Unsupported file type: {file_extension}")
    except Exception as e:
        print(f"Failed to load file: {e}")
        return None
