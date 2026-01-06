import os
from datetime import datetime, timedelta

import torch
from config import cfg
from src.learner import Learner

learner = Learner(graph_path=cfg.COMMUNE.GRAPH_PATH,
                  max_iteration=cfg.COMMUNE.MAX_ITERATION)


def remove_contents(path):
    os.makedirs(path, exist_ok=True)
    file_lists = os.listdir(path)
    if file_lists is not None:
        for f in file_lists:
            fp = os.path.join(path, f)
            if os.path.isfile(fp):
                os.remove(fp)
    return True


def compute_date_range():
    start_raw = cfg.RUNNER.START_DATE
    if start_raw:
        start_dt = datetime.strptime(start_raw, "%d/%m/%Y")
    else:
        start_dt = datetime.today()

    if cfg.RUNNER.TIME_DELTA is not None:
        end_dt = start_dt + timedelta(days=int(cfg.RUNNER.TIME_DELTA))
    else:
        end_raw = getattr(cfg.RUNNER, "END_DATE", None)
        if not end_raw:
            raise ValueError(
                "Either RUNNER.TIME_DELTA or RUNNER.END_DATE must be set")
        end_dt = datetime.strptime(end_raw, "%d/%m/%Y")

    return start_dt.strftime("%d/%m/%Y"), end_dt.strftime("%d/%m/%Y")


def main():
    start_date, end_date = compute_date_range()

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
    else:
        raise ValueError(
            f"Invalid RUNNER.MODE: {mode}. Expected one of: commune, province, Hanoi"
        )

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
