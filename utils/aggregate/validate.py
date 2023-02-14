import pandas as pd
import gzip
import pickle
import torch


def validate(path):
    with gzip.open("./original_data.pkl.gz", 'rb') as f:
        _, loc2id, _ = pickle.load(f)
    df = pd.read_excel("./patients.xlsx")
    err = []
    for loc in df.iloc[:, 1:].to_numpy():
        try:
            loc2id[(loc[1], loc[2], loc[3])]
        except KeyError:
            err.append((loc[0], loc[1], loc[2], loc[3]))
    err_df = pd.DataFrame.from_records(
        err, columns=['MCB', 'Xã/Phường', 'Quận/Huyện', 'Tỉnh/TP'])
    err_df.sort_values(by=['Tỉnh/TP', 'Quận/Huyện', 'Xã/Phường']).to_excel(
        'error.xlsx', index=False)
