"""Reproduce the supplementary waiting and policy comparisons in Sections 5.1 and 5.3."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t

from src.models.channel import Config, generate
from src.models.simulator import simulate


def fallback_comparison(config, seed):
    busy, eligible = generate(config, seed)
    age, age_trace = simulate(config, busy, eligible, 'AgeAware', return_trace=True)
    fallback, fallback_trace = simulate(config, busy, eligible, 'ProbeThen20', return_trace=True)
    return {
        'AgeAware_goodput_Mbps': age['goodput_mbps'],
        'ProbeThen20_goodput_Mbps': fallback['goodput_mbps'],
        'AgeAware_minus_ProbeThen20_Mbps': age['goodput_mbps'] - fallback['goodput_mbps'],
        'different_mask_frames': np.count_nonzero(age_trace['action'] != fallback_trace['action']),
    }


def waiting_comparison(config, seed):
    busy, eligible = generate(config, seed)
    result, trace = simulate(config, busy, eligible, 'AgeAware', return_trace=True)
    waits = trace['completed_wait_frames']
    return {
        'AgeAware_zero_wait_completed_cycles_pct': 100 * np.mean(waits == 0) if waits.size else np.nan,
        'AgeAware_failed_frames_pct': 100 * result['fail_count'] / config.n,
    }


def summarize(config, seeds, measure):
    values_by_seed = pd.DataFrame([measure(config, seed) for seed in seeds], index=seeds)
    for metric, values in values_by_seed.items():
        yield {
            'k': config.k,
            'duty': config.duty,
            'rho': config.rho,
            'probe_interval_frames': config.probe_interval,
            'frames_per_seed': config.n,
            'metric': metric,
            **{f'seed_{seed}': value for seed, value in values.items()},
            'mean': values.mean(),
            'ci95_half_width': t.ppf(0.975, values.count() - 1) * values.sem(),
        }


def main():
    root = Path(__file__).resolve().parent
    settings = json.loads((root / 'config/experiments.json').read_text(encoding='utf-8'))
    seeds = settings['seeds']
    rows = []
    for rho in settings['sensitivity_rhos']:
        config = Config(n=settings['n'], k=3, duty=0.6, rho=rho, probe_interval=25)
        rows.extend(summarize(config, seeds, fallback_comparison))
    main_config = Config(n=settings['n'], k=3, duty=0.3,
                         rho=settings['rho'], probe_interval=settings['probe_interval'])
    rows.extend(summarize(main_config, seeds, waiting_comparison))
    output = root / 'results/supplementary_analysis.csv'
    output.parent.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False, float_format='%.12g')
    print(f'Wrote {output.relative_to(root)}')


if __name__ == '__main__':
    main()
