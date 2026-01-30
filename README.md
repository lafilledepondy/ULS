# Uncapacitated Lot Sizing (ULS)

Implementation of two integer programming models that solve the Uncapacitated Lot Sizing problem with setup costs using the HiGHS optimizer (`highspy`). The script reads every instance in `Instances_ULS/`, solves it with the selected formulation, and exports LaTeX-ready summary tables.

## Requirements

- Python 3.10+
- `highspy` and `pandas` (`pip install highspy pandas`).

## Usage

1. Drop `.txt` instances in `Instances_ULS/` (format: periods, per-period demand, production cost, setup cost, inventory cost).
2. Run `python main.py` to process all instances with `solve_model_2` (switch to `solve_model_1` inside `main.py` if needed).
3. Collect detailed logs in the console and LaTeX tables in `model1_results.tex` / `model2_results.tex`.

## Files

- `main.py`: orchestrates batch solving and report generation.
- `helperFunctions.py`: parsing utilities, solution pretty-printers, LaTeX exporter.
- `modelisations.py`: model definitions for both formulations (production-inventory and assignment-based).
- `Instances_ULS/`: sample benchmark instances from 21 to 120 periods plus a toy case.
