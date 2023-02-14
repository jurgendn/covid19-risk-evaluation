import gzip
import pickle

import torch
from tqdm.auto import tqdm

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class RiskModel:

    def __init__(self,
                 graph_path: str,
                 max_iteration: int = 30000,
                 walk_length: int = 20,
                 batch_size: int = 10000,
                 duration_threshold: int = 9) -> None:

        # Initilise hyperparameters
        with gzip.open(graph_path, 'rb') as f:
            _, _, proba_matrix = pickle.load(f)
            self.graph = proba_matrix.to(device)

        self.max_iteration: int = max_iteration
        self.walk_length: int = walk_length
        self.duration_threshold: int = duration_threshold
        self.batch_size: int = batch_size

        # Initialise attributes
        self.position = torch.Tensor([])
        self.batch_position = torch.Tensor([])

    def __get_next_move(self) -> torch.Tensor:
        current_position = self.batch_position[:, -1].reshape(-1, 1)
        proba_matrix_at_positions = self.graph[current_position]
        proba_matrix_at_positions = proba_matrix_at_positions.reshape(
            proba_matrix_at_positions.shape[0],
            proba_matrix_at_positions.shape[2])
        transition_proba = torch.rand(size=(proba_matrix_at_positions.shape[0],
                                            1)).to(device)
        mask = torch.where(proba_matrix_at_positions >= transition_proba, 1, 0)
        move_list = torch.argmax(mask, 1)
        next_move = move_list.reshape(-1, 1)
        next_move = next_move - 1
        return next_move

    def __update_postion(self) -> None:
        next_move = self.__get_next_move()
        self.batch_position = torch.cat(
            tensors=[self.batch_position, next_move], axis=1)

    def fit(self, initial_position: torch.Tensor) -> None:
        gpu_output = torch.tensor([]).to(device)
        self.output = torch.tensor([], dtype=torch.int16)
        for _ in tqdm(range(1, self.max_iteration + 1)):
            self.position = initial_position
            batches = self.position.shape[0] // self.batch_size + 1
            split_point = [batch * self.batch_size for batch in range(batches)]
            split_point.append(self.position.shape[0])
            for i in range(len(split_point) - 1):
                gpu_output = torch.tensor([]).to(device)
                self.batch_position = self.position[
                    split_point[i]:split_point[i + 1]]
                for walk in range(self.walk_length):
                    self.__update_postion()
                gpu_output = torch.cat(
                    tensors=[gpu_output, self.batch_position], dim=0)
                self.output = torch.cat(tensors=[
                    self.output,
                    gpu_output.to('cpu').to(torch.int16)
                ],
                                        dim=0)
                del gpu_output
