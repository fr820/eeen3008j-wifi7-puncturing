import numpy as np
import pytest
from dataclasses import replace
from src.models.channel import Config,generate,idle_probability
from src.models.simulator import simulate
from src.baselines.policies import MASKS,NAMES

def clean(c): return np.zeros((c.n,4),bool),np.zeros(4,bool)

@pytest.mark.parametrize('policy',NAMES)
def test_no_interference_closed_form(policy):
 c=Config(n=100,k=0)
 r=simulate(c,*clean(c),policy)
 rate=80 if policy=='Fixed20' else 320
 expected=rate*(1-c.cca_ms-c.signal_ms-c.probe_ms/c.probe_interval-(c.compute_ms if policy=='AgeAware' else 0))
 assert r['goodput_mbps']==pytest.approx(expected)
 assert r['fail_count']==0 and r['wait_p95_ms']==0

def test_zero_overhead_four_to_one():
 c=Config(n=50,k=0,cca_ms=0,probe_ms=0,signal_ms=0,puncture_ms=0,switch_ms=0,compute_ms=0)
 a=simulate(c,*clean(c),'Wait80')['goodput_mbps']
 b=simulate(c,*clean(c),'Fixed20')['goodput_mbps']
 assert a/b==pytest.approx(4)

@pytest.mark.parametrize('policy',NAMES)
def test_primary_busy_forces_wait(policy):
 c=Config(n=100); b=np.zeros((100,4),bool); b[:,0]=1
 r=simulate(c,b,np.ones(4,bool),policy)
 assert r['delivered_bits']==0 and r['defer_count']==100
 assert np.isnan(r['wait_p95_ms']) and r['censored_tail_ms']==100

def test_exactly_one_secondary_busy():
 c=Config(n=100,k=1,duty=1,probe_interval=1)
 b=np.zeros((100,4),bool); b[:,2]=1
 e=np.array([0,0,1,0],bool)
 assert simulate(c,b,e,'Wait80')['goodput_mbps']==0
 for p in ['Greedy','AgeAware']:
  r,t=simulate(c,b,e,p,True)
  assert np.all(t['action']==2) and r['fail_count']==0

def test_two_secondaries_busy_uses_fallback():
 c=Config(n=100,duty=1,probe_interval=1)
 b=np.tile([0,1,1,0],(100,1)).astype(bool)
 for p in ['Greedy','AgeAware']:
  r,t=simulate(c,b,np.array([0,1,1,0],bool),p,True)
  assert np.all(t['action']==4)

@pytest.mark.parametrize('policy',NAMES)
def test_conservation_and_budgets(policy):
 c=Config(n=1000); b,e=generate(c,19)
 r,t=simulate(c,b,e,policy,True)
 assert r['attempted_bits']==pytest.approx(r['delivered_bits']+r['failed_bits'])
 assert r['tx_count']+r['defer_count']==c.n
 assert r['success_count']+r['fail_count']==r['tx_count']
 assert np.all((t['overhead']>=0)&(t['overhead']<1))
 assert 0<=r['goodput_mbps']<=sum(c.rate_mbps)
 assert 0<=r['unused_clear_mhz']<=r['mean_clear_mhz']

def test_seed_reproduction():
 c=Config(n=500); a,e=generate(c,5); b,f=generate(c,5)
 assert np.array_equal(a,b) and np.array_equal(e,f)
 assert simulate(c,a,e,'AgeAware')==simulate(c,b,f,'AgeAware')

def test_stationarity_and_transition():
 c=Config(n=100000,k=3,duty=.3,rho=.8)
 b,e=generate(c,500)
 assert np.max(np.abs(b[:,e].mean(0)-.3))<.025
 assert abs(np.mean(b[1:,1][~b[:-1,1]])-.06)<.01

def test_prediction_endpoints():
 c=Config(n=2,duty=.3,rho=0)
 m=np.array([[0,0,1,0],[0,0,1,0]],bool)
 q=idle_probability(m,np.array([0,1]),c,np.ones(4,bool))
 assert q[0,1]==1 and q[0,2]==0
 assert np.allclose(q[1,1:],.7)
 assert np.all((q>=0)&(q<=1))

def test_masks_keep_primary_and_valid_width():
 assert MASKS[:,0].all()
 assert set(MASKS.sum(1))=={1,3,4}

def test_invalid_config():
 for kw in [dict(duty=1.1),dict(k=4),dict(rho=-.1),dict(probe_interval=0),dict(signal_ms=2)]:
  with pytest.raises(ValueError): Config(**kw)

def test_clear_bandwidth_identity():
 c=Config(n=50,k=0); r=simulate(c,*clean(c),'Fixed20')
 assert r['unused_clear_mhz']==60 and r['mean_clear_mhz']==80
