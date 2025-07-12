import api
from excel.reader import read_excel_data
from logic.processor import process_row

if __name__ == "__main__":
    file_path = "excel/data.xlsx"
    df = read_excel_data(file_path)

    for _, row in df.iterrows():
        process_row(row.to_dict())