import gzip
import pickle
from datetime import datetime, timedelta
from itertools import chain

import numpy as np
import pandas as pd
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class InitialPatients:

    def __init__(self,
                 graph_path: str = None,
                 threshold_date: int = 10) -> None:

        self.raw_data = None
        self.patient_list = None

        self.__threshold_date = threshold_date

        if graph_path is not None:
            with gzip.open(graph_path, 'rb') as f:
                _, self.__loc2id, _ = pickle.load(f)

    def __get_datetime_col(self):
        for i, col in enumerate(self.raw_data.columns[3:]):
            if isinstance(col, datetime) is False:
                return i + 3

    def __data_converter(self):
        columns = self.raw_data.columns[3:]

        columns = list(map(lambda x: datetime.strftime(x, "%d/%m/%Y"),
                           columns))
        df_cols = list(self.raw_data.columns[:3]) + columns

        self.raw_data.columns = df_cols
        columns = self.raw_data.columns[3:]

        patients_list = {col: [] for col in columns}

        MCB = 0

        for i, col in enumerate(columns):
            tmp = self.raw_data.iloc[:, [0, 1, 2, i + 3]]
            tmp = tmp[tmp[col] != 0]
            for _, row in tmp.iterrows():
                row[3] = int(row[3])
                for dup in range(row[3]):
                    MCB += 1
                    patients_list[col].append([
                        col, MCB, row[2].strip(), row[1].strip(),
                        row[0].strip()
                    ])
        patients_list = list(chain.from_iterable(patients_list.values()))
        patients_list = list(map(tuple, patients_list))
        self.patient_list = pd.DataFrame(patients_list,
                                         columns=[
                                             'Ngày công bố', "MCB",
                                             "Xã/Phường", "Quận/Huyện",
                                             "Tỉnh/TP"
                                         ])

    def read_file(self,
                  path: str,
                  file_type: str = 'excel',
                  input_type: str = 'full'):
        if input_type == 'full':
            self.patient_list = pd.read_excel(path)
        else:
            if file_type == 'excel':
                df = pd.read_excel(path, sheet_name=None)
                self.raw_data = pd.DataFrame()
                for sheetname, sheetval in df.items():
                    self.raw_data = pd.concat(
                        [self.raw_data, pd.DataFrame(sheetval)])
                self.raw_data = self.raw_data.iloc[:, :self.__get_datetime_col(
                )].replace(np.nan, np.int32(0)).reset_index().iloc[:, 1:]
                self.__data_converter()
            else:
                print("Invalid file format")

    def get_initial_position(self, target_date: str, level: str = 'commune'):
        patient_arr = self.patient_list.to_numpy()
        patient_arr = np.array(
            list(
                filter(
                    lambda x: datetime.strptime(target_date, '%d/%m/%Y') -
                    datetime.strptime(x[0], '%d/%m/%Y') < timedelta(
                        days=self.__threshold_date), patient_arr)))
        if level == 'commune':
            return torch.tensor([
                self.__loc2id.get((loc[0], loc[1], loc[2]), -1)
                for loc in patient_arr[:, 2:]
            ]).reshape(-1, 1).to(device)
        elif level == 'district':
            return torch.tensor([
                self.__loc2id.get((loc[1], loc[2]), -1)
                for loc in patient_arr[:, 2:]
            ]).reshape(-1, 1).to(device)
        elif level == 'province':
            return torch.tensor([
                self.__loc2id.get(loc[2], -1) for loc in patient_arr[:, 2:]
            ]).reshape(-1, 1).to(device)
