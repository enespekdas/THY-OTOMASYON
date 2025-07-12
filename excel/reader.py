import pandas as pd
import os

def read_excel_data(file_path: str) -> pd.DataFrame:
    """
    Verilen Excel dosyasını okur ve pandas DataFrame döner.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel dosyası bulunamadı: {file_path}")

    df = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')
    return df
