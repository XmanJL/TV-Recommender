import joblib
import json
import numpy as np
from os import path

def convert_joblib_to_json(joblib_filepath, json_filepath):
    """
    Converts a joblib file to a JSON file.

    Args:
        joblib_filepath (str): Path to the joblib file.
        json_filepath (str): Path to the output JSON file.
    """
    try:
        data = joblib.load(path.join("model", joblib_filepath))
    except Exception as e:
        raise ValueError(f"Could not load joblib file: {e}")
    
    def convert_np_to_list(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: convert_np_to_list(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [convert_np_to_list(elem) for elem in obj]
        return obj

    data = convert_np_to_list(data)
    
    try:
        with open(json_filepath, 'w') as f:
            records = data.to_json(orient='records')
            f.write(records)
    except Exception as e:
         raise ValueError(f"Could not write JSON file: {e}")

if __name__ == "__main__":
    convert_joblib_to_json('titles.joblib', 'model/titles.json')
    convert_joblib_to_json('titles_.joblib', 'model/titles_2.json')