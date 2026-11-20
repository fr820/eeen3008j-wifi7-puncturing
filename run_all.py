"""Run the tests and reproduce the simulation data, figures, and results page."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys

from src.experiments.run import run
from src.visualization.illustrations import create as create_illustrations
from src.visualization.plots import create as create_plots
from src.visualization.results_page import write_results_page


def main():
    root = Path(__file__).resolve().parent
    subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests'], cwd=root, check=True)
    raw, summary = run(root)
    create_plots(root, summary)
    create_illustrations(root)

    data_files = (
        'results/raw_data/runs.csv',
        'results/raw_data/trace_manifest.csv',
        'results/summary.csv',
        'results/paired_comparisons.csv',
    )
    hashes = {
        str(Path(name)): hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in data_files
    }
    (root / 'results/data_sha256.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    write_results_page(root, raw, summary)
    print('Completed. Open results/index.html to view the figures and data.')


if __name__ == '__main__':
    main()
