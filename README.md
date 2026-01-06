# covid19-risk-evaluation

[![Python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)](#requirements)
[![PyTorch](https://img.shields.io/badge/PyTorch-used-EE4C2C?logo=pytorch&logoColor=white)](#requirements)
[![Thesis PDF](https://img.shields.io/badge/thesis-PDF-0F9D58?logo=googledrive&logoColor=white)](https://drive.google.com/file/d/1XfyhQYO1oogcgXU4GNUXGb8USVILmzMv/view?usp=sharing)
[![Status](https://img.shields.io/badge/status-research%20code-6c757d)](#)

Network / random-walk based COVID-19 risk evaluation for Vietnam (research code).

## Thesis

This repository implements the core ideas described in the thesis:

**“Mô hình mạng lưới và ứng dụng xác định nguy cơ trong đại dịch COVID-19 tại Việt Nam”**
(Network Model and Its Application in Assessing Risk During the COVID-19 Pandemic in Vietnam)

- PDF: https://drive.google.com/file/d/1XfyhQYO1oogcgXU4GNUXGb8USVILmzMv/view?usp=sharing

## What this code does

At a high level:

- Administrative regions are represented as nodes in a graph.
- A (possibly weighted) random walk on that graph approximates how infection exposure “diffuses” across regions.
- For each day in a requested date range, the model:
	1) selects patients within a recent time window (default: 7 days),
	2) runs many random-walk simulations starting from those patients’ locations,
	3) aggregates visit counts into a risk score per region,
	4) writes daily risk tables to Excel.

The main runnable entrypoint is `main.py`.

## Algorithm (thesis)

Let $G=(V,E,w)$ be a region graph. Each infected individual is modeled as a random walker on $G$ with a Markov transition matrix $W$.

### Time window ($d_0$)

On a target date $t$, only patients with detection date $d_i$ satisfying $t-d_i \le d_0$ contribute to risk.
In this repo, this is implemented as `duration_threshold` (defaulted to 7 in `main.py`).

### Algorithm 1 — Single random-walk simulation

For each patient (walker):

1. Initialize at the patient’s home node.
2. Perform a random walk of length $L$ steps.
3. Count visits per node across all walkers.
4. Normalize visit counts to obtain a risk vector $R$ over nodes.

In code, $L$ corresponds to `walk_length`.

### Algorithm 2 — Monte Carlo averaging

Because Algorithm 1 is stochastic, repeat it $M$ times and average:

$$
R = \frac{1}{M} \sum_{m=1}^{M} R_m
$$

In this repo:

- `max_iteration` corresponds to the number of Monte Carlo repetitions $M$.
- `epochs` repeats the whole date-range run multiple times (producing multiple output files per day).

## Repository structure

- `main.py`: runs training/simulation for a configured date range and level
- `config/params.py`: configuration (paths, date range, mode)
- `src/walk_model.py`: random-walk simulation (`RiskModel`)
- `src/initial_parameters.py`: patient filtering + mapping locations to node IDs
- `src/post_process.py`: aggregates visits and writes Excel outputs
- `utils/`: helper scripts for data cleaning/aggregation (optional)

## Requirements

- Python 3.9+ recommended
- Packages: see `requirements.txt`

Notes:

- `torch` is used for the walk simulation (CPU works; CUDA is optional).
- Input graphs and patient data are **not** included in this repository; you must provide them.

## Quickstart (local)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run
python main.py
```

## Configuration

Edit `config/params.py`.

### Runner settings

`RUNNER` controls the global run:

- `MODE`: one of `commune`, `province`, `Hanoi`
- `DATA_PATH`: path to the patient Excel file (default: `./data/patients.xlsx`)
- `START_DATE`: start date in `dd/mm/YYYY` (if empty/None, uses “today”)
- `TIME_DELTA`: number of days to run from `START_DATE`
- `END_DATE`: optional alternative to `TIME_DELTA` (used when `TIME_DELTA` is None)

### Level settings

Each level section (`COMMUNE`, `PROVINCE`, `HANOI`) provides:

- `GRAPH_PATH`: path to the pre-built graph file
- `OUTPUT_PATH`: folder where daily Excel outputs are written
- `MAX_ITERATION`, `WALK_LENGTH`, `EPOCHS`: simulation hyperparameters
- `LEVEL_NAME`: mapping level used to interpret patient locations (`commune` / `province`)

## Input data formats

### 1) Graph file (`*.pkl.gz`)

`GRAPH_PATH` must point to a gzip-compressed pickle containing a tuple:

1. `id2loc`: mapping from node id (int) -> location label (string or tuple)
2. `loc2id`: mapping from location label -> node id
3. `proba_matrix`: a Torch tensor encoding transition probabilities per node

The random-walk model loads it in `src/walk_model.py`.

### 2) Patients file (`*.xlsx`)

By default (`Learner.get_patients(..., input_type='full')`) the code expects a “long” table with columns:

- `Ngày công bố` (dd/mm/YYYY)
- `MCB` (patient id; any unique-ish value)
- `Xã/Phường`
- `Quận/Huyện`
- `Tỉnh/TP`

The `src/initial_parameters.py` loader filters patients by recency (the last `duration_threshold` days).

#### Converting a “wide” daily-count workbook

If your patient workbook is in a “wide” format (dates as columns, counts per row), you can convert it to the “long” format using:

```bash
python utils/helpers/input_converter.py
```

Adjust the input/output paths inside that script as needed.

## Output

For each date (and each epoch), the pipeline writes an Excel file:

- Path: `{OUTPUT_PATH}/{DD_MM_YYYY}_{epoch}.xlsx`
- Columns:
	- `Location`
	- `<date>` (risk score)

The current implementation outputs a scaled proportion (per 10,000 visits) computed from random-walk visit counts.

## Running with Docker

`docker-compose.yml` defines a service that runs `python main.py`.

```bash
docker compose up --build
```

Make sure you mount/provide the expected folders (`data/`, graph files, and `output/`).

## Utility scripts (optional)

Under `utils/aggregate/` there are helpers for:

- normalizing raw patient spreadsheets (`preprocessing.py`)
- merging multi-sheet inputs (`merge_input.py`)
- generating daily pivot-style stats (`get_stats.py`)

These are not required to run `main.py`, but can help prepare inputs.
