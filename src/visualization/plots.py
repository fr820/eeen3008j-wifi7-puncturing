import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyArrowPatch
from src.baselines.policies import NAMES
COLORS=['#64748b','#c07823','#087e8b','#912d54']
def create(root,s):
 plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'font.family':'DejaVu Sans'})
 dest=root/'results/figures'
 dest.mkdir(parents=True,exist_ok=True)
 def save(fig,name):
  fig.savefig(dest/(name+'.png'),dpi=220,bbox_inches='tight'); fig.savefig(dest/(name+'.pdf'),bbox_inches='tight'); plt.close(fig)
 for metric,ylabel,name in [('goodput_mbps','Unique-payload goodput (Mbps)','figure_1_goodput'),('wait_p95_ms','Run-level 95th-percentile service wait (ms)','figure_2_wait'),('unused_clear_mhz','Unused clear bandwidth (MHz)','figure_3_unused')]:
  fig,axs=plt.subplots(1,3,figsize=(12,3.8),sharey=True)
  for k,ax in zip([1,2,3],axs):
   for policy,col in zip(NAMES,COLORS):
    g=s[(s.scenario=='main')&(s.k==k)&(s.policy==policy)].sort_values('duty')
    ax.errorbar(g.duty,g[metric+'_mean'],yerr=g[metric+'_ci95'],label=policy,color=col,marker='o',capsize=3)
   ax.set_title(f'K = {k} potentially busy blocks'); ax.set_xlabel('Interference duty cycle'); ax.set_xticks([.1,.3,.6]); ax.grid(alpha=.2)
  axs[0].set_ylabel(ylabel); axs[-1].legend(fontsize=9)
  fig.suptitle('Mean and 95% t intervals across 10 independent runs',fontsize=12); fig.tight_layout(); save(fig,name)
 fig,axs=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
 for rho,ax in zip([.2,.9],axs):
  for p,col in zip(NAMES,COLORS):
   g=s[(s.scenario=='stale')&(s.rho==rho)&(s.policy==p)].sort_values('interval')
   ax.errorbar(g.interval,g.goodput_mbps_mean,yerr=g.goodput_mbps_ci95,label=p,color=col,marker='o',capsize=3)
  ax.set_title(f'Occupancy correlation rho = {rho}'); ax.set_xlabel('Secondary measurement interval (ms)'); ax.grid(alpha=.2)
 axs[0].set_ylabel('Goodput (Mbps)'); axs[1].legend(fontsize=9); fig.tight_layout(); save(fig,'figure_4_staleness')
 fig,axs=plt.subplots(1,2,figsize=(10.8,3.85))
 stress_ids=['clean','primary','overhead','mismatch','unequal']
 stress_labels=['No interference','Primary busy','High signalling','Wrong model','Unequal rates']
 for ax,metric,label in [(axs[0],'goodput_mbps','Goodput (Mbps)'),(axs[1],'fail_rate','Failed transmission fraction')]:
  for i,(p,col) in enumerate(zip(NAMES,COLORS)):
   g=s[(s.scenario.isin(stress_ids))&(s.policy==p)].set_index('scenario').loc[stress_ids]
   ax.bar(np.arange(5)+(i-1.5)*.18,g[metric+'_mean'],width=.18,yerr=g[metric+'_ci95'],label=p,color=col,capsize=2)
  ax.set_xticks(range(5),stress_labels,rotation=16,ha='right'); ax.set_ylabel(label); ax.grid(axis='y',alpha=.2)
 axs[0].legend(fontsize=8.5); fig.tight_layout(); save(fig,'figure_5_stress')
 fig,ax=plt.subplots(figsize=(10,4)); ax.set_xlim(0,10); ax.set_ylim(0,4); ax.axis('off')
 blocks=[(.2,2.3,2.1,'Occupancy chains\n4 x 20 MHz'),(3,2.3,2.5,'Primary CCA\nSecondary probes'),(6.2,2.3,3.4,'Wait80 / Fixed20 / Greedy\nAgeAware expected reward'),(6.2,.3,3.4,'Mask, airtime and collision\nGoodput, wait, unused MHz')]
 for x,y,w,label in blocks:
  ax.add_patch(Rectangle((x,y),w,1,fc='#e8eff4',ec='#34495e')); ax.text(x+w/2,y+.5,label,ha='center',va='center',fontsize=11)
 for a,b in [((2.3,2.8),(3,2.8)),((5.5,2.8),(6.2,2.8)),((7.9,2.3),(7.9,1.3))]: ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=16,color='#34495e'))
 ax.text(.3,.7,'Shared fixed 1 ms frames\nSame traces and overhead rules\nPrimary remains active in every mask',fontsize=11)
 save(fig,'system_model')
