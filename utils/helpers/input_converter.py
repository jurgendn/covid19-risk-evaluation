import pandas as pd
import numpy as np
from datetime import datetime
from itertools import chain


def get_col(data):
    for i, col in enumerate(data.columns[3:]):
        if isinstance(col, datetime) is False:
            return i + 3


def create_data(file_name):
    patients_summary = pd.read_excel(file_name, sheet_name=None)
    data = pd.DataFrame()
    for sheetname, sheetval in patients_summary.items():
        data = pd.concat([data, pd.DataFrame(sheetval)])
    data = data.drop(labels='Tổng', axis=1)
    return data


def create_df(file_name: str = './input/CaBenhTinhThanh.xlsx'):
    data = create_data(file_name)
    data = data.iloc[:, :get_col(data)].replace(np.nan, np.int32(0))
    columns = data.columns[3:]
    columns = list(map(lambda x: datetime.strftime(x, "%d/%m/%Y"), columns))
    df_cols = list(data.columns[:3]) + columns
    data.columns = df_cols
    columns = data.columns[3:]
    final_list = {col: [] for col in columns}
    MCB = 0

    for i, col in enumerate(columns):
        tmp = data.iloc[:, [0, 1, 2, i + 3]]
        tmp = tmp[tmp[col] != 0]
        for _, row in tmp.iterrows():
            row[3] = int(row[3])
            for dup in range(row[3]):
                MCB += 1
                final_list[col].append([col, MCB, row[2], row[1], row[0]])
    final_final_df = final_list.values()
    final_final_df = list(chain.from_iterable(final_final_df))
    final_final_df = list(map(tuple, final_final_df))

    return final_final_df


if __name__ == "__main__":
    final_df = create_df(file_name='./input/CaBenhTinhThanh.xlsx')
    print(len(final_df))
    pd.DataFrame(
        final_df,
        columns=['Ngày công bố', "MCB", "Xã/Phường", "Quận/Huyện",
                 "Tỉnh/TP"]).to_excel("./output/patients_new.xlsx",
                                      index=False)
