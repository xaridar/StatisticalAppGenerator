import pandas as pd
import numpy as np

def calc(string):
    return {"Text": string, "DT": pd.DataFrame({'n': np.linspace(1, 50, num=50), 'e': np.linspace(2, 100, 50)})}