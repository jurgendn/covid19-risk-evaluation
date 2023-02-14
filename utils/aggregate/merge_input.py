import os
from copy import deepcopy

import pandas as pd
from tqdm.notebook import tqdm


class MergeInput:

    def __init__(self) -> None:
        self.data = None
        self.raw_sheets = []

    def __read_file__(self, folder_path: str):
        file_list = os.listdir(folder_path)
        for file in tqdm(file_list):
            if file.endswith(".xlsx"):
                try:
                    print(f"--- Reading file ---")
                    print(f"{folder_path}{file}")
                    self.raw_sheets.append(
                        pd.read_excel(folder_path + file, sheet_name=None))
                except OverflowError:
                    print(f"Overflow at: {file}")
                finally:
                    print(f"Error: {file}")

    def __merge_data__(self):
        self.data = deepcopy(self.raw_sheets[0])
        for sheet in self.raw_sheets[1:]:
            for sheet_name, sheet_data in sheet.items():
                if len(sheet_data.columns) > 30:
                    self.data[sheet_name] = sheet_data

    def __write_data__(self, target_folder: str, file_name: str):
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        with pd.ExcelWriter(target_folder + file_name + ".xlsx") as writer:
            for sheet_name, sheet_val in tqdm(self.data.items()):
                sheet_val.to_excel(writer, sheet_name=sheet_name, index=False)

    def fit(self, folder_path: str, target_folder: str, file_name: str):
        self.__read_file__(folder_path)
        self.__merge_data__()
        self.__write_data__(target_folder, file_name)
        return True
