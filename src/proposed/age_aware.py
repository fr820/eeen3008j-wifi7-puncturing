import numpy as np
from src.baselines.policies import MASKS, observed_feasible
from src.models.channel import idle_probability

def choices(measured,age,c,eligible,probe_cost):
    q=idle_probability(measured,age,c,eligible)
    probability=np.prod(np.where(MASKS[None,:,:],q[:,None,:],1.),axis=2)
    rates=MASKS @ np.array(c.rate_mbps)
    # Charge a conservative switching allowance to every candidate.
    available=c.frame_ms-c.cca_ms-probe_cost[:,None]-c.signal_ms-c.compute_ms-c.switch_ms
    available=available-c.puncture_ms*(MASKS.sum(axis=1)==3)
    expected=probability*rates*available/c.frame_ms
    scores=np.where(observed_feasible(measured),expected,-np.inf)
    return np.argmax(scores,axis=1)
