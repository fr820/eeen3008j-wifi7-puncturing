"""Write a self-contained entry page for the local simulation results."""

import csv
from html import escape

from src.baselines.policies import NAMES


PERFORMANCE_FIGURES = (
    ('figure_1_goodput', 'Goodput across interference settings'),
    ('figure_4_staleness', 'Sensitivity to the secondary measurement interval'),
    ('figure_2_wait', '95th-percentile service waiting time'),
    ('figure_3_unused', 'Unused clear bandwidth'),
    ('figure_5_stress', 'Stress cases and model sensitivity'),
)


def write_results_page(root, raw, summary):
    """Build the English overview from the current run's data and figures."""
    settings = ['scenario', 'k', 'duty', 'rho', 'interval']
    scenario_count = len(raw[settings].drop_duplicates())
    trace_count = len(raw[settings + ['seed']].drop_duplicates())
    main = summary.loc[(summary.scenario == 'main') & (summary.k == 2) & (summary.duty == 0.3)]
    stale = summary.loc[(summary.scenario == 'stale') & (summary.rho == 0.2) & (summary.interval == 25)]
    main = main.set_index('policy')
    stale = stale.set_index('policy')

    def goodput(frame, policy):
        if policy not in frame.index:
            return 'Unavailable'
        row = frame.loc[policy]
        return f'{row.goodput_mbps_mean:.2f} ± {row.goodput_mbps_ci95:.2f}'

    rows = '\n'.join(
        f'<tr><th scope="row">{escape(policy)}</th><td>{goodput(main, policy)}</td>'
        f'<td>{goodput(stale, policy)}</td></tr>'
        for policy in NAMES
    )
    results = root / 'results'
    with (results / 'paired_comparisons.csv').open(encoding='utf-8', newline='') as file:
        paired = next((r for r in csv.DictReader(file)
                       if r['scenario'] == 'stale' and r['baseline'] == 'Greedy'
                       and float(r['rho']) == 0.2 and int(r['interval']) == 25), None)
    comparison = ''
    if paired is not None:
        comparison = ('<p>In the 25 ms case, the paired goodput difference for AgeAware versus '
                      f'Greedy is <strong>{float(paired["delta_mbps"]):.2f} ± '
                      f'{float(paired["ci95_mbps"]):.2f} Mbps</strong>. The difference is '
                      f'{float(paired["gain_percent"]):.2f}% relative to Greedy’s mean.</p>')

    figures = '\n'.join(
        f'<figure><figcaption>{escape(caption)}</figcaption>'
        f'<img src="figures/{name}.png" alt="{escape(caption)}" loading="lazy"></figure>'
        for name, caption in PERFORMANCE_FIGURES
    )
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Group 18 Wi-Fi 7 Simulation Results</title>
<style>
body {{ margin: 28px auto; max-width: 1040px; padding: 0 20px;
  font: 16px/1.55 system-ui, sans-serif; color: #183044; background: #f8fafc; }}
h1, h2 {{ line-height: 1.2; }} a {{ color: #075487; }}
table {{ border-collapse: collapse; width: 100%; background: white; }}
th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid #cbd7e2; }}
thead {{ background: #e5eef6; }}
figure {{ margin: 20px 0; padding: 12px; background: white; border: 1px solid #cbd7e2; }}
figcaption {{ font-weight: 600; }} img {{ display: block; width: 100%; height: auto; }}
</style>
</head>
<body><main>
<h1>Wi-Fi 7 Puncturing Simulation Results</h1>
<p>EEEN3008J, Group 18, Topic 02</p>
<p>Completed {scenario_count} experiment settings, {trace_count} shared interference traces and {len(raw)} policy runs.</p>
<h2>Goodput in two representative settings</h2>
<p>Mean ± half-width of the 95% confidence interval, in Mbps.</p>
<table>
<thead><tr><th scope="col">Policy</th><th scope="col">Main sweep<br>K = 2, duty cycle = 0.3</th>
<th scope="col">Rapidly changing interference<br>Occupancy correlation = 0.2, 25 ms probe interval</th></tr></thead>
<tbody>{rows}</tbody>
</table>
{comparison}
<p><a href="summary.csv">Full summary</a> | <a href="paired_comparisons.csv">Paired comparisons</a> |
<a href="raw_data/runs.csv">Run-level data</a> | <a href="raw_data/trace_manifest.csv">Trace manifest</a> |
<a href="environment.json">Run environment</a> | <a href="data_sha256.json">Data checksums</a></p>
<h2>Performance figures</h2>
{figures}
</main></body></html>'''
    (results / 'index.html').write_text(html, encoding='utf-8')
