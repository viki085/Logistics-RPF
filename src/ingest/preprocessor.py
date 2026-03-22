import pandas as pd
from src.config.schema import CURRENCIES
import re


class Preprocessor:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def extract_header(self) -> list:
        return self.df.columns.tolist()

    def resolve_combined_columns(self, df: pd.DataFrame) -> pd.DataFrame:

        for col in df.columns[:-1]:
            split = df[col].astype(str).str.split()

            first = split.str[0]
            last = split.str[-1]

            mask = last.isin(CURRENCIES)

            df.loc[mask, col] = first

        return df
    
    def preprocess_header(self, header: list) -> list:
        clean_header = []
        currency_pattern = r'\b(' + '|'.join(CURRENCIES) + r')\b'
        columns = self.extract_header()
        for col in columns:
            col = re.sub(currency_pattern, '', col, flags=re.IGNORECASE)
            col = col.replace("_", " ").replace("-", " ")
            col = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', col)   # camelCase → camel Case    
            col = re.sub(r'(?<=[A-Za-z])(?=\d)', ' ', col)   # letters→digits: "20gp" stays, "type20" → "type 20"     # digits→letters: "20gp" → "20 gp"    
            col = re.sub(r'\s+', ' ', col)  
            col = re.sub(r'[()]', '', col)                 # collapse spaces     
            col = col.lower().strip()
            clean_header.append(col)
        return clean_header




    
            

            
        
        
    