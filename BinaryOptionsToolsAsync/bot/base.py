import pandas as pd

class BaseBot:
    def __init__(self):
        pass

    def get_data(self, timestamp: int) -> pd.DataFrame:
        pass
    
    def predict_trade(self, data: pd.DataFrame) -> String:
        pass