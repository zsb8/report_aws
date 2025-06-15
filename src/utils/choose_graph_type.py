import os
import sys
import io
from pathlib import Path
import pandas as pd
import json
from typing import List, Dict
# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.aws_utilities import is_aws_environment, read_file_from_s3, save_text_to_s3


def parse_csv_json(csv_json: str) -> pd.DataFrame:
    obj = json.loads(csv_json)
    df = pd.DataFrame(obj["rows"], columns=obj["headers"])
    return df

def classify_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    numeric_cols, categorical_cols = [], []
    for col in df.columns:
        try:
            pd.to_numeric(df[col])
            numeric_cols.append(col)
        except ValueError:
            categorical_cols.append(col)
    return {"numeric": numeric_cols, "categorical": categorical_cols}

def top_k_by_cardinality(df: pd.DataFrame, cols: List[str], k: int = 3, ascending: bool = True) -> List[str]:
    uniq_counts = {c: df[c].nunique(dropna=False) for c in cols}
    sorted_cols = sorted(uniq_counts, key=uniq_counts.get, reverse=not ascending)
    return sorted_cols[:k]

def recommend_axes(csv_json: str, graph_types: List[str]) -> Dict[str, Dict[str, List[str]]]:
    df = parse_csv_json(csv_json)
    col_types = classify_columns(df)

    recs = {}
    for g in graph_types:
        if g == "bar":
            x_cols = top_k_by_cardinality(df, col_types["categorical"], k=3, ascending=True)
            y_cols = col_types["numeric"][:3] or ["<row_count>"]
        elif g == "line":
            x_candidates = col_types["numeric"] + col_types["categorical"]
            x_cols = top_k_by_cardinality(df, x_candidates, k=3, ascending=False)
            y_cols = col_types["numeric"][:3]
        elif g == "scatter":
            x_cols = col_types["numeric"][:3]
            y_cols = col_types["numeric"][:3]
        else:
            raise ValueError(f"暂不支持图形类型: {g}")
        recs[g] = {"x_candidates": x_cols, "y_candidates": y_cols}
    return recs


def choose_graph_type(csv_json, graph_types):
    try:
        if isinstance(csv_json, dict):
            print("!!!!====Converting dict to JSON string")
            csv_json = json.dumps(csv_json)
        elif isinstance(csv_json, str):
            print("!!!!====Input is already a string")
            try:
                json.loads(csv_json)
            except json.JSONDecodeError:
                print("!!!!====Invalid JSON string, trying to convert to dict first")
                try:
                    csv_json = eval(csv_json)
                    csv_json = json.dumps(csv_json)
                except:
                    raise ValueError("Input is neither a valid JSON string nor a valid Python dict")
        else:
            raise ValueError(f"Unsupported input type: {type(csv_json)}")
            
        print(f"!!!!====Processed csv_json: {csv_json}")
        
        if is_aws_environment():
            print("!!!!====Running in AWS environment")
            print(f"!!!!====Input JSON: {csv_json}, Input graph_types: {graph_types}")
            result = recommend_axes(csv_json, graph_types)
        else:
            print("!!!!====Running in local environment")
            result = recommend_axes(csv_json, graph_types)
            print(f"!!!!====result: {result}")
            
        return (result, None)

    except Exception as e:
        error_msg = f"Error processing : {str(e)}"
        print(f"!!!!====Error occurred: {error_msg}")
        return (None, error_msg)

if __name__ == "__main__":
    csv_data ={
        "headers": ["id", "first_name", "last_name", "salary", "departmen"],
        "rows": [
            ["1", "John", "Smith", "20000", "Reportin"],
            ["2", "Ian", "Peterson", "80000", "Engineerin"],
            ["3", "Mike", "Peterson", "20000", "Engineerin"],
            ["4", "Cailin", "Ninson", "30000", "Engineerin"],
            ["5", "John", "Mills", "50000", "Marketin"],
            ["6", "Ava", "Muffinson", "10000", "Silly Walks\r"]
        ]
    }
    csv_json = json.dumps(csv_data)
    graph_types=['bar', 'line','scatter']
    result, error = choose_graph_type(csv_json, graph_types)
    if is_aws_environment():
        pass
    else:
        print(result) 

