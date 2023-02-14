import pickle
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


class GetStatistics:

    def __init__(self, threshhold: int = 7) -> None:
        self.__threshhold = threshhold
        self.data = None
        self.sheets = {}

    def __get_patients(self):

        def parse_date(s):
            return datetime.strptime(s, "%d/%m/%Y")

        cols = self.data.columns
        self.data = np.array(
            list(
                filter(
                    lambda s: datetime.today() - parse_date(s[0]) <= timedelta(
                        days=self.__threshhold), self.data.to_numpy())))
        self.data = pd.DataFrame(self.data, columns=cols)

    def __read_file(self, file_path: str):
        self.data = pd.read_excel(file_path)

    def __groupby(self) -> None:

        with open("./provinces_list.pkl", "rb") as f:
            provinces = pickle.load(f)
        data_provinces = sorted(self.data["Tỉnh/TP"].dropna().unique())

        provinces = sorted(
            list(set(provinces).intersection(set(data_provinces))))

        for prv in provinces:
            prv_data = self.data[self.data['Tỉnh/TP'] == prv].groupby(
                by=['Tỉnh/TP', 'Quận/Huyện', 'Xã/Phường', 'Ngày công bố'
                    ]).count().unstack()
            prv_data.columns = prv_data.columns.get_level_values(1)
            self.sheets[prv] = prv_data.transpose().sort_index().transpose()

    def fit(self, file_path: str):
        self.__read_file(file_path)
        self.data['MCB'] = "Values"
        self.data = self.data.dropna(subset=['Ngày công bố'])
        self.__get_patients()
        self.__groupby()
        return True

    def to_file(self, output_path: str):
        with pd.ExcelWriter(output_path) as f:
            for sheet_name, sheet_val in self.sheets.items():
                try:
                    sheet_val.to_excel(f, sheet_name, merge_cells=False)
                except IndexError:
                    pass
