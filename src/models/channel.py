"""Independent two-state occupancy chains on a shared fixed-time grid."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Config:
    n: int = 30000
    k: int = 2
    duty: float = .3
    rho: float = .9
    probe_interval: int = 5
    frame_ms: float = 1.
    cca_ms: float = .01
    probe_ms: float = .05
    signal_ms: float = .04
    puncture_ms: float = .02
    switch_ms: float = .02
    compute_ms: float = .005
    rate_mbps: tuple = (80., 80., 80., 80.)
    primary_busy: bool = False
    assumed_rho: float = -1.
    def __post_init__(self):
        if not (0 <= self.k <= 3 and 0 <= self.duty <= 1 and 0 <= self.rho <= 1):
            raise ValueError('Invalid channel parameters')
        if self.n < 1 or self.probe_interval < 1 or len(self.rate_mbps) != 4:
            raise ValueError('Invalid dimensions')
        if any(x < 0 for x in self.rate_mbps): raise ValueError('Negative rate')
        costs = (self.cca_ms,self.probe_ms,self.signal_ms,self.puncture_ms,self.switch_ms,self.compute_ms)
        if any(x < 0 for x in costs) or sum(costs) >= self.frame_ms:
            raise ValueError('Overheads must fit inside one frame')

def generate(c, seed):
    rng = np.random.default_rng(seed)
    eligible = np.zeros(4, dtype=bool)
    if c.k:
        ids = np.r_[0, rng.permutation([1,2,3])[:c.k-1]] if c.primary_busy else rng.permutation([1,2,3])[:c.k]
        eligible[ids] = True
    busy = np.zeros((c.n,4), dtype=bool)
    busy[0] = (rng.random(4) < c.duty) & eligible
    draws = rng.random((c.n-1,4))
    # Stationary busy probability d, lag-one correlation rho.
    for t in range(1,c.n):
        p = np.where(busy[t-1], c.duty+(1-c.duty)*c.rho, c.duty*(1-c.rho))
        busy[t] = (draws[t-1] < p) & eligible
    return busy, eligible

def idle_probability(measured, age, c, eligible):
    rho = c.rho if c.assumed_rho < 0 else c.assumed_rho
    q = 1-c.duty+(c.duty-measured.astype(float))*rho**age[:,None]
    q[:,~eligible] = 1.
    q[:,0] = 1. # Immediate primary CCA is enforced separately.
    return q
