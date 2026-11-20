import numpy as np
# Keysight non-OFDMA 80 MHz table, excluding punctured primary 20 MHz.
# 1000 is a separate conventional 20 MHz fallback, not an 80 MHz puncture.
MASKS = np.array([[1,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,0],[1,0,0,0]], dtype=bool)
NAMES = ['Wait80','Fixed20','Greedy','AgeAware']

def observed_feasible(measured):
    return ~np.any(measured[:,None,:] & MASKS[None,:,:],axis=2)

def baseline_choices(measured, name):
    feasible = observed_feasible(measured)
    n=len(measured)
    if name=='Wait80': return np.where(feasible[:,0],0,-1)
    if name=='Fixed20': return np.full(n,4,dtype=int)
    if name=='Greedy':
        scores=np.where(feasible,MASKS.sum(axis=1),-1)
        return np.argmax(scores,axis=1)
    raise ValueError(name)
