import pandas as pd
from datetime import datetime
from time import time

from src.initial_parameters import InitialPatients
from src.post_process import PostProcess
from src.walk_model import RiskModel


class Learner:

    def __init__(self,
                 graph_path: str = None,
                 max_iteration: int = 10000,
                 walk_length: int = 20,
                 batch_size: int = 10000,
                 duration_threshold: int = 10) -> None:

        self.max_iteration = max_iteration
        self.walk_length = walk_length
        self.duration_threshold = duration_threshold
        self.graph_path = graph_path

        self.model: RiskModel = RiskModel(
            graph_path=graph_path,
            max_iteration=max_iteration,
            walk_length=walk_length,
            batch_size=batch_size,
            duration_threshold=duration_threshold)

        self.post_processor = PostProcess(graph_path=graph_path)

        self.initializer = InitialPatients(graph_path=graph_path,
                                           threshold_date=duration_threshold)

    def get_patients(self, patient_path: str = "", input_type: str = 'full'):
        self.initializer.read_file(patient_path, input_type)

    def fit(self,
            start_date: str,
            end_date: str,
            epoches: int = 5,
            level: str = 'commune',
            output_path: str = "/content/drive/MyDrive/covid/output"):
        s_date = datetime.strptime(start_date, "%d/%m/%Y")
        e_date = datetime.strptime(end_date, "%d/%m/%Y")
        daterange = pd.date_range(s_date, e_date)
        for epoch in range(epoches):
            for date in daterange:
                print(f"----------Date: {date}----------")
                exec_time = time()
                date = datetime.strftime(date, '%d/%m/%Y')
                patient_list = self.initializer.get_initial_position(
                    target_date=date, level=level)
                self.model.fit(patient_list)
                res = self.model.output
                file_name = '_'.join(date.split("/"))
                file_name = f"{file_name}_{epoch}"
                self.post_processor.fit(res,
                                        target_date=date,
                                        file_name=file_name,
                                        output_path=output_path)
                print(f"Execution Time: {time() - exec_time}")
