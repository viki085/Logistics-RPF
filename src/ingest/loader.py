import os
import pandas as pd

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = None
        self.file_extension = os.path.splitext(file_path)[1]

    def load(self) -> pd.DataFrame:
        if self.file_extension == ".xlsx":
            self.df = pd.read_excel(self.file_path)
        elif self.file_extension == ".csv":
            self.df = pd.read_csv(self.file_path)
        return self.df
    
    def get_columns(self) -> list:
        return self.df.columns.tolist()
    
    def get_data(self) -> pd.DataFrame:
        return self.df
    
    def save(self, output_path: str) -> None:
        self.df.to_csv(output_path, index=False)

