import pandas as pd

try:
    df = pd.read_csv("datasets/superstore.csv", encoding="latin1")

    print("="*50)
    print("Dataset Loaded Successfully")
    print("="*50)

    print(df.columns)

    print(df.head())

except Exception as e:
    print(e)