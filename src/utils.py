import pandas as pd

def clean_data(df):
    df.drop_duplicates(inplace=True)
    df.fillna(method='ffill', inplace=True)
    return df

def normalize_data(df):
    # Example normalization
    df['ip'] = df['ip'].str.strip()
    return df
