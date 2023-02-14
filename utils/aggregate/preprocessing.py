import re
from unicodedata import normalize

import pandas as pd


class PreProcessing:

    def __init__(self) -> None:
        pass

    def __get_data__(self, path: str = "./Bảng Tổng Hợp F0-Toàn Quốc.xlsx"):
        df = pd.read_excel(path, sheet_name=None)
        cols = [1, 2, 7, 8, 9]
        data = pd.DataFrame()
        for sheet_name, sheet_val in df.items():
            sheet_val = sheet_val.iloc[:, cols]
            data = pd.concat([data, sheet_val], axis=0)
        self.data = data.reset_index().iloc[:, 1:]
        self.data.columns = [
            "Ngày công bố", "MCB", "Xã/Phường", "Quận/Huyện", "Tỉnh/TP"
        ]

    def __normailize_date(self):

        def to_string(s):
            try:
                return s.strftime("%d/%m/%Y")
            except:
                return s

        self.data["Ngày công bố"] = self.data["Ngày công bố"].map(to_string)

    def __normalize_location(self):

        def remove_prefix(s):
            if pd.isna(s) or not isinstance(s, str):
                return s
            s = normalize("NFKC", s)
            if re.match(r"Phường [0-9]", s) or re.match(r"Quận [0-9]", s):
                s = re.sub(r"Phường 0", "Phường ", s)
                return s
            s = re.sub(r"Phường 0", "Phường ", s)
            s = re.sub(r"Phường ", "", s)
            s = re.sub(r"Quận ", "", s)
            s = re.sub(r"Tỉnh ", "", s)
            s = re.sub(r"Huyện ", "", s)
            s = re.sub(r"Thị trấn ", "", s)
            s = re.sub(r"Thị Trấn ", "", s)
            s = re.sub(r"Thị xã ", "", s)
            s = re.sub(r"Thị Xã ", "", s)
            s = re.sub(r"Thành phố ", "", s)
            s = re.sub(r"TP. ", "", s)
            s = re.sub(r"TP ", "", s)
            s = re.sub(r" - ", " ", s)
            s = re.sub(r"-", " ", s)
            s = re.sub(r"Xã ", "", s)
            s = re.sub(r"xã ", "", s)
            s = re.sub(r"TT. ", "", s)
            s = re.sub(r"TT ", "", s)
            s = re.sub(r"HCM", "Hồ Chí Minh", s)
            s = re.sub(r"Thành phô Hồ Chí Minh", "Hồ Chí Minh", s)
            s = s.strip().title()
            return s

        def fix_parenthesis(s):
            if pd.isna(s) or not isinstance(s, str):
                return s
            s = re.sub(r"Hoà\s", "Hòa ", s)
            s = re.sub(r"Hoà$", "Hòa", s)
            return s

        self.data.iloc[:, 2:] = self.data.iloc[:, 2:].applymap(
            remove_prefix).applymap(fix_parenthesis)

    def __fix_old_loc(self):

        def fix_old_location(s):
            if pd.isna(s) or not isinstance(s, str):
                return s
            s = re.sub("Quận 2", "Thủ Đức", s)
            s = re.sub("Quận 9", "Thủ Đức", s)
            return s

        self.data[self.data.loc[:, "Tỉnh/TP"] == "Hồ Chí Minh"] = self.data[
            self.data.loc[:, "Tỉnh/TP"] == "Hồ Chí Minh"].applymap(
                fix_old_location)

    def fit(self, path: str):
        self.__get_data__(path)
        self.__normailize_date()
        self.__normalize_location()
        self.__fix_old_loc()
        self.data = self.data.dropna(subset=['Ngày công bố'])

    def to_file(self, output_path: str):
        self.data.to_excel(output_path, index=False)
