import os
from datetime import datetime, timedelta

import torch
from config import cfg
from src.learner import Learner

learner = Learner(graph_path=cfg.COMMUNE.GRAPH_PATH,
                  max_iteration=cfg.COMMUNE.MAX_ITERATION)


def remove_contents(path):
    file_lists = os.listdir(path)
    if file_lists is not None:
        for f in file_lists:
            os.remove(f"{path}/{f}", )
    return True


def main():
    if cfg.RUNNER.START_DATE is None:
        assert cfg.RUNNER.TIME_DELTA is not None
        start_date = datetime.today().strftime("%d/%m/%Y")
        end_date = (start_date +
                    timedelta(days=cfg.RUNNER.TIME_DELTA)).strftime("%d/%m/%Y")
        start_date = start_date.strftime("%d/%m/%Y")
    else:
        start_date = datetime.strptime(cfg.RUNNER.START_DATE, "%d/%m/%Y")
        end_date = (start_date +
                    timedelta(days=cfg.RUNNER.TIME_DELTA)).strftime("%d/%m/%Y")
        start_date = start_date.strftime("%d/%m/%Y")

    mode = cfg.RUNNER.MODE

    if mode == "commune":
        graph_path = cfg.COMMUNE.GRAPH_PATH
        output_path = cfg.COMMUNE.OUTPUT_PATH
        max_iteration = cfg.COMMUNE.MAX_ITERATION
        walk_length = cfg.COMMUNE.WALK_LENGTH
        epochs = cfg.COMMUNE.EPOCHS
        level = cfg.COMMUNE.LEVEL_NAME
    elif mode == 'province':
        graph_path = cfg.PROVINCE.GRAPH_PATH
        output_path = cfg.PROVINCE.OUTPUT_PATH
        max_iteration = cfg.PROVINCE.MAX_ITERATION
        walk_length = cfg.PROVINCE.WALK_LENGTH
        epochs = cfg.PROVINCE.EPOCHS
        level = cfg.PROVINCE.LEVEL_NAME
    elif mode == 'Hanoi':
        graph_path = cfg.HANOI.GRAPH_PATH
        output_path = cfg.HANOI.OUTPUT_PATH
        max_iteration = cfg.HANOI.MAX_ITERATION
        walk_length = cfg.HANOI.WALK_LENGTH
        epochs = cfg.HANOI.EPOCHS
        level = cfg.HANOI.LEVEL_NAME

    torch.cuda.empty_cache()
    remove_contents(output_path)
    learner = Learner(graph_path=graph_path,
                      max_iteration=max_iteration,
                      walk_length=walk_length,
                      batch_size=10000,
                      duration_threshold=7)
    learner.get_patients(patient_path=cfg.RUNNER.DATA_PATH)
    learner.fit(start_date=start_date,
                end_date=end_date,
                epoches=epochs,
                level=level,
                output_path=output_path)


if __name__ == "__main__":
    main()
