import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Pipeline.preprocesamiento import preprocess_data


import pandas as pd
# tests/test_preprocess.py
from Pipeline.preprocesamiento import preprocess_data

def test_fill_missing_values():
    data = {"rooms": [2, None, 3]}
    result = preprocess_data(data)
    assert result["rooms"].isnull().sum() == 0

#para que corra este test hay que correr: pytest -v tests/test_preprocess.py
#en la terminal!!!!
