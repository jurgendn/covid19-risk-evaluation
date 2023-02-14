import gzip
import pickle

import pandas as pd
import torch


class PostProcess:

    def __init__(self, graph_path: str = None) -> None:
        if graph_path is not None:
            with gzip.open(graph_path, 'rb') as f:
                self.id2loc, _, _ = pickle.load(f)

    def fit(self,
            input: torch.Tensor,
            target_date: str = None,
            file_name: str = None,
            output_path: str = "/content/drive/MyDrive/covid/output"):
        counter = torch.unique(input, return_counts=True)
        proportion_val = {
            self.id2loc.get(int(key), f"Error: {key}"):
            float(10000 * val / torch.sum(counter[1]))
            for key, val in zip(counter[0], counter[1])
        }
        self.res = pd.DataFrame(proportion_val.items(),
                                columns=['Location', target_date])
        self.res.to_excel(f'{output_path}/{file_name}.xlsx', index=False)
