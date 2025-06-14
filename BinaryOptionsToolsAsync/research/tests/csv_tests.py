import pandas as pd

test_dataframe = ["win", "win", "win", "win", "win", "win", "win", "loss", "loss", "loss", "loss", "loss"]

df = pd.DataFrame(data=test_dataframe)
df.columns = ["trade_result"]
print(df)
df.to_csv("test_csv1__wdwd_.csv")