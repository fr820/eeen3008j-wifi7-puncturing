from dataclasses import replace,asdict
from pathlib import Path
import hashlib,json,platform,sys
import numpy as np
import pandas as pd
from scipy.stats import t
from src.models.channel import Config,generate
from src.models.simulator import simulate
from src.baselines.policies import NAMES

METRICS=['goodput_mbps','wait_mean_ms','wait_p95_ms','unused_clear_mhz','unrecovered_clear_mhz','fail_rate','defer_fraction','overhead_fraction']
def aggregate(raw,keys):
 out=[]
 for key,g in raw.groupby(keys,dropna=False):
  row=dict(zip(keys,key if isinstance(key,tuple) else [key]))
  for m in METRICS:
   vals=g[m].dropna(); n=len(vals)
   row[m+'_mean']=vals.mean(); row[m+'_std']=vals.std(ddof=1)
   row[m+'_ci95']=t.ppf(.975,n-1)*vals.std(ddof=1)/np.sqrt(n) if n>1 else np.nan
   row[m+'_n']=n
  out.append(row)
 return pd.DataFrame(out)

def run(root):
 settings=json.loads((root/'config/experiments.json').read_text())
 raw_dir=root/'results/raw_data'
 raw_dir.mkdir(parents=True,exist_ok=True)
 base=Config(n=settings['n']); scenarios=[]
 for k in settings['k']:
  for duty in settings['duty']: scenarios.append(('main',replace(base,k=k,duty=duty)))
 for rho in settings['sensitivity_rhos']:
  for interval in settings['sensitivity_intervals']:
   scenarios.append(('stale',replace(base,k=3,duty=.6,rho=rho,probe_interval=interval)))
 scenarios += [('clean',replace(base,k=0,duty=0)),('primary',replace(base,k=1,duty=.6,primary_busy=True)),
               ('overhead',replace(base,k=1,duty=.3,puncture_ms=.35)),
               ('mismatch',replace(base,k=3,duty=.6,rho=.2,probe_interval=25,assumed_rho=.99)),
               ('unequal',replace(base,k=2,duty=.3,rate_mbps=(80,40,100,60)))]
 rows=[]; traces=[]
 for scenario,c in scenarios:
  for seed in settings['seeds']:
   busy,eligible=generate(c,seed)
   digest=hashlib.sha256(busy.tobytes()).hexdigest()
   traces.append(dict(scenario=scenario,k=c.k,duty=c.duty,rho=c.rho,interval=c.probe_interval,seed=seed,sha256=digest,eligible=''.join(map(str,eligible.astype(int)))))
   for policy in NAMES:
    rows.append(dict(scenario=scenario,k=c.k,duty=c.duty,rho=c.rho,interval=c.probe_interval,seed=seed,policy=policy,**simulate(c,busy,eligible,policy)))
 raw=pd.DataFrame(rows)
 raw.to_csv(raw_dir/'runs.csv',index=False,float_format='%.12g')
 pd.DataFrame(traces).to_csv(raw_dir/'trace_manifest.csv',index=False)
 keys=['scenario','k','duty','rho','interval','policy']
 summary=aggregate(raw,keys)
 summary.to_csv(root/'results/summary.csv',index=False,float_format='%.12g')
 pairs=[]
 for key,g in raw.groupby(keys[:-1]):
  pivot=g.pivot(index='seed',columns='policy',values='goodput_mbps')
  for other in ['Wait80','Fixed20','Greedy']:
   delta=pivot.AgeAware-pivot[other]; n=len(delta)
   pairs.append(dict(zip(keys[:-1],key),baseline=other,delta_mbps=delta.mean(),ci95_mbps=t.ppf(.975,n-1)*delta.std(ddof=1)/np.sqrt(n),gain_percent=100*(pivot.AgeAware.mean()/pivot[other].mean()-1) if pivot[other].mean() else np.nan))
 pd.DataFrame(pairs).to_csv(root/'results/paired_comparisons.csv',index=False,float_format='%.12g')
 versions={}
 from importlib.metadata import version
 for pkg in ['numpy','pandas','scipy','matplotlib','pytest']:
  versions[pkg]=version(pkg)
 (root/'results/environment.json').write_text(json.dumps(dict(python=sys.version,platform=platform.platform(),packages=versions,base_config=asdict(base),settings=settings),indent=2))
 (root/'requirements.txt').write_text('\n'.join(f'{k}=={v}' for k,v in versions.items())+'\n')
 print(f'{len(scenarios)} scenarios, {len(raw)} policy runs, {len(traces)} shared traces')
 return raw,summary
