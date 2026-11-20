import numpy as np
from src.baselines.policies import MASKS, baseline_choices
from src.proposed.age_aware import choices

def simulate(c,busy,eligible,policy,return_trace=False):
    if busy.shape != (c.n,4): raise ValueError('Trace dimensions differ')
    t=np.arange(c.n)
    age=t % c.probe_interval
    measured=busy[t-age].copy()
    measured[:,0]=False # All methods receive the same immediate primary CCA.
    probe_cost=(age==0)*c.probe_ms
    if policy == 'AgeAware':
        action = choices(measured, age, c, eligible, probe_cost)
    elif policy == 'ProbeThen20':
        action = baseline_choices(measured, 'Fixed20')
        on_probe = age == 0
        action[on_probe] = baseline_choices(measured[on_probe], 'Greedy')
    else:
        action = baseline_choices(measured, policy)
    action[busy[:,0]]=-1
    tx=action>=0
    active=np.zeros_like(busy)
    active[tx]=MASKS[action[tx]]
    # Remember the last transmitted mask across deferred frames.
    last_tx=np.maximum.accumulate(np.where(tx,t,-1))
    previous_idx=np.r_[-1,last_tx[:-1]]
    previous_action=np.full(c.n,-1)
    ok=previous_idx>=0
    previous_action[ok]=action[previous_idx[ok]]
    switched=tx & (previous_action>=0) & (action!=previous_action)
    punctured=tx & (active.sum(axis=1)==3)
    signal=tx*c.signal_ms+punctured*c.puncture_ms
    compute=np.full(c.n,c.compute_ms if policy=='AgeAware' else 0.)
    overhead=c.cca_ms+probe_cost+signal+switched*c.switch_ms+compute
    data_ms=(c.frame_ms-overhead)*tx
    success=tx & ~np.any(active & busy,axis=1)
    capacity=active @ np.array(c.rate_mbps)
    # Mbps * ms = kilobits; convert to bits explicitly.
    offered_bits=capacity*data_ms*1000
    delivered=offered_bits*success
    lost=offered_bits*(tx & ~success)
    clear=~busy
    unused=20*np.sum(clear & ~active,axis=1)
    effective_clear=20*np.sum(clear,axis=1)-20*np.sum(active,axis=1)*success*data_ms/c.frame_ms
    successes=np.flatnonzero(success)
    # Complete service cycles only; retain censored trailing cycle separately.
    waits=np.diff(np.r_[-1,successes])-1
    tail=c.n-1-successes[-1] if len(successes) else c.n
    result={
      'goodput_mbps':float(delivered.sum()/(c.n*c.frame_ms*1000)),
      'wait_mean_ms':float(waits.mean()*c.frame_ms) if len(waits) else np.nan,
      'wait_p95_ms':float(np.percentile(waits,95)*c.frame_ms) if len(waits) else np.nan,
      'unused_clear_mhz':float(unused.mean()),
      'unrecovered_clear_mhz':float(effective_clear.mean()),
      'fail_rate':float(np.sum(tx & ~success)/tx.sum()) if tx.any() else 0.,
      'defer_fraction':float((~tx).mean()),
      'overhead_fraction':float(overhead.mean()/c.frame_ms),
      'delivered_bits':float(delivered.sum()),'failed_bits':float(lost.sum()),
      'attempted_bits':float(offered_bits.sum()),
      'tx_count':int(tx.sum()),'success_count':int(success.sum()),
      'defer_count':int((~tx).sum()),'fail_count':int((tx & ~success).sum()),
      'censored_tail_ms':float(tail*c.frame_ms),
      'mean_clear_mhz':float(20*clear.sum(axis=1).mean()),
    }
    if return_trace: return result,dict(action=action,success=success,overhead=overhead,data_ms=data_ms,delivered_bits=delivered,completed_wait_frames=waits)
    return result
