# Group 18 Wi-Fi 7 Puncturing Simulation

EEEN3008J Wireless Communications, Topic 02

Open [results/index.html](results/index.html) in a browser to see the verified run, goodput comparison, and five performance figures. The page links to the full CSV data, environment record, and checksums. The package also contains the terminal output in `reference_run_log.txt`.

## Reproduce the results

Extract the ZIP and open a terminal in the folder containing `run_all.py`. The reference run used 64-bit Python 3.12 on Windows. Internet access is needed to install the listed dependencies. The simulation runs locally after installation.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_all.py
```

On macOS or Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_all.py
```

The script runs 21 tests, evaluates 22 settings across 220 shared interference traces and 880 policy runs, then rebuilds the data, figures, and `results/index.html`. Open the page after the completion message. The `results/` folder initially contains the verified run included with this ZIP.

To reproduce the supplementary comparisons in Sections 5.1 and 5.3, run `python run_supplement.py` with the same virtual-environment interpreter. The script writes [results/supplementary_analysis.csv](results/supplementary_analysis.csv). Each seed column gives one run's value. The last two columns give the mean and the half-width of its 95% Student-t interval across seeds. `ProbeThen20` uses Greedy on probe frames and the primary 20 MHz otherwise. Goodput differences subtract this rule from AgeAware within each seed. Mask differences count frames, and zero-wait percentages use completed service cycles.

## Inspect the code and data

- `src/` contains the Python simulation, policies, and plotting code. `config/experiments.json` defines the settings and `tests/` contains the model checks.
- `results/summary.csv` contains the aggregate statistics and confidence intervals. `results/paired_comparisons.csv` contains the within-seed goodput differences. `results/raw_data/` contains individual runs and the shared trace manifest.
- `reference_data_sha256.json` records the four data file checksums used in the report. Match each file by name against `results/data_sha256.json`. Path separators, CSV line endings, and floating-point rounding can differ across platforms.
- `input/original_matlab/` includes the team's MATLAB prototype with English comments. Cached Live Editor previews were removed from this copy. The Python simulation produced the results in `results/`.
