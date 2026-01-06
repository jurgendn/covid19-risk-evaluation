from dataclasses import dataclass


@dataclass
class RUNNER:
    MODE = 'commune'
    DATA_PATH = "./data/patients.xlsx"
    START_DATE = "01/07/2021"
    END_DATE = "06/07/2021"
    TIME_DELTA = 5
    INPUT_PATH = "./data/patients.xlsx"


@dataclass
class COMMUNE:
    GRAPH_PATH = "./resources/original_data.pkl.gz"
    OUTPUT_PATH = "output/commune"
    MAX_ITERATION = 1000
    WALK_LENGTH = 20
    EPOCHS = 4
    LEVEL_NAME = "commune"


@dataclass
class PROVINCE:
    GRAPH_PATH = "./resources/province_data.pkl.gz"
    OUTPUT_PATH = "output/province"
    MAX_ITERATION = 1000
    WALK_LENGTH = 20
    EPOCHS = 4
    LEVEL_NAME = "province"


@dataclass
class HANOI:
    GRAPH_PATH = "./resources/province_data.pkl.gz"
    OUTPUT_PATH = "output/Hanoi"
    MAX_ITERATION = 1000
    WALK_LENGTH = 20
    EPOCHS = 4
    LEVEL_NAME = "commune"