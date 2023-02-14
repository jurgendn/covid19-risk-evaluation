import pickle
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


class GetStatistics:

    def __init__(self, thresh_hold: int = 7) -> None:
        self.__threshold = thresh_hold
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
                        days=self.__threshold), self.data.to_numpy())))
        self.data = pd.DataFrame(self.data, columns=cols)

    def __read_file(self, file_path: str):
        self.data = pd.read_excel(file_path)

    def __group_by_commune(self):
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
            prv_data.columns = pd.to_datetime(prv_data.columns,
                                              format="%d/%m/%Y")
            prv_data = prv_data.transpose().sort_index().transpose()
            prv_data.columns = list(
                map(lambda s: s.strftime("%d/%m/%Y"), prv_data.columns))
            self.sheets[prv] = prv_data

    def __group_by_district(self):
        with open("./provinces_list.pkl", "rb") as f:
            provinces = pickle.load(f)
        data_provinces = sorted(self.data["Tỉnh/TP"].dropna().unique())

        provinces = sorted(
            list(set(provinces).intersection(set(data_provinces))))

        for prv in provinces:
            prv_data = self.data[self.data['Tỉnh/TP'] == prv].groupby(
                by=['Tỉnh/TP', 'Quận/Huyện', 'Ngày công bố'
                    ]).count().unstack()
            prv_data.columns = prv_data.columns.get_level_values(1)
            prv_data.columns = pd.to_datetime(prv_data.columns,
                                              format="%d/%m/%Y")
            prv_data = prv_data.transpose().sort_index().transpose()
            prv_data.columns = list(
                map(lambda s: s.strftime("%d/%m/%Y"), prv_data.columns))
            self.sheets[prv] = prv_data

    def __group_by_province(self):
        with open("./provinces_list.pkl", "rb") as f:
            provinces = pickle.load(f)
        data_provinces = sorted(self.data["Tỉnh/TP"].dropna().unique())

        provinces = sorted(
            list(set(provinces).intersection(set(data_provinces))))

        prv_data = self.data.groupby(by=['Tỉnh/TP', 'Ngày công bố']).count()
        prv_data.drop(columns=['Xã/Phường', 'Quận/Huyện'],
                      axis=1,
                      inplace=True)
        prv_data = prv_data.unstack()
        prv_data.columns = prv_data.columns.get_level_values(1)
        prv_data.columns = pd.to_datetime(prv_data.columns, format="%d/%m/%Y")
        prv_data = prv_data.transpose().sort_index().transpose()
        filtered = prv_data.loc[prv_data.index.isin(provinces)]
        filtered.columns = list(
            map(lambda s: s.strftime("%d/%m/%Y"), prv_data.columns))
        self.sheets['Data'] = filtered

    def __groupby(self, level: str = 'commune') -> None:

        if level == 'commune':
            self.__group_by_commune()
        elif level == 'district':
            self.__group_by_district()
        elif level == 'province':
            self.__group_by_province()

    def fit(self, file_path: str, level: str = 'commune'):
        self.__read_file(file_path)
        self.data['MCB'] = "Values"
        self.data = self.data.dropna(subset=['Ngày công bố'])
        self.__get_patients()
        self.__groupby(level=level)
        return True

    def to_file(self, output_path: str):
        with pd.ExcelWriter(output_path) as f:
            for sheet_name, sheet_val in self.sheets.items():
                try:
                    sheet_val.to_excel(f, sheet_name, merge_cells=False)
                except IndexError:
                    pass
