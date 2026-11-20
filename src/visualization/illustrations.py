"""Conceptual diagrams for the 80 MHz puncturing and staleness model.

Run with python -m src.visualization.illustrations from the project root.
PNG for Word plus SVG/PDF for scalable reuse are generated deterministically.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch, Arc

INK='#203547'; BLUE='#2877b5'; TEAL='#0b8490'; ORANGE='#d58a26'
RED='#a33d55'; GREY='#e7edf2'; OUTLINE='#97a8b7'; WHITE='#ffffff'

def setup(width,height):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'svg.fonttype':'none'})
    f,a=plt.subplots(figsize=(width,height)); a.set_xlim(0,10);a.set_ylim(0,height)
    a.axis('off'); f.subplots_adjust(left=.01,right=.99,bottom=.02,top=.98)
    return f,a

def label(a,x,y,t,size=13,color=INK,ha='center',weight='normal',va='center'):
    return a.text(x,y,t,fontsize=size,color=color,ha=ha,va=va,weight=weight,linespacing=1.25)

def arrow(a,start,end,color=OUTLINE,style='-',width=1.6):
    a.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=16,
                              linewidth=width,color=color,linestyle=style))

def rect(a,x,y,w,h,color,edge=None,hatch=None):
    a.add_patch(Rectangle((x,y),w,h,facecolor=color,edgecolor=edge or WHITE,
                         linewidth=1.2,hatch=hatch))

def save(f,root,name):
    dest=root/'results/figures';dest.mkdir(exist_ok=True,parents=True)
    for ext in ['png','pdf','svg']:
        f.savefig(dest/f'{name}.{ext}',dpi=300,facecolor='white',bbox_inches='tight',pad_inches=.06)
    plt.close(f)

def spectrum(root):
    f,a=setup(10,3.05)
    panels=[(.16,'(a) Desired channel','80 MHz nominal'),
            (3.6,'(b) Partial interference','One secondary block is busy'),
            (7.04,'(c) Punctured transmission','60 MHz remains active')]
    for n,(x,title,sub) in enumerate(panels):
        label(a,x+1.36,2.8,title,14,weight='bold')
        for k in range(4):
            sx=x+k*.68
            busy=n>0 and k==2
            poly=Polygon([(sx+.03,.91),(sx+.14,1.87),(sx+.56,1.87),(sx+.65,.91)],
                         closed=True,facecolor=ORANGE if busy else BLUE,
                         edgecolor=ORANGE if busy else BLUE,linewidth=1.3,
                         hatch='////' if busy else None,alpha=.20 if n==2 and busy else 1)
            a.add_patch(poly)
            if busy:
                label(a,sx+.34,2.13,'Interferer',10,ORANGE)
            label(a,sx+.34,.66,['P','S1','S2','S3'][k],12,weight='bold' if k==0 else 'normal')
        arrow(a,(x,.86),(x+2.74,.86),INK,width=.9)
        label(a,x+1.36,.29,sub,11.8)
    arrow(a,(2.99,1.43),(3.48,1.43),OUTLINE,width=2.3)
    arrow(a,(6.43,1.43),(6.93,1.43),OUTLINE,width=2.3)
    # A muted block is a hole in the active pattern, not a reduction of channel spacing.
    save(f,root,'concept_puncturing')

def topology(root):
    f,a=setup(10,3.9)
    # Saturated payload source.
    for j in range(3): rect(a,.25+j*.11,2.22+j*.14,.75,.4,BLUE)
    label(a,.78,1.83,'Payload source\n(saturated)',12)
    arrow(a,(1.35,2.6),(2.24,2.6),INK)
    # AP router with physical antenna cues.
    rect(a,2.3,2.22,1.2,.45,TEAL,TEAL)
    for x in [2.47,3.31]:
        a.plot([x,x-.1],[2.67,3.16],color=TEAL,lw=2.2)
    for j in range(3): a.plot(2.6+j*.25,2.44,'o',color=WHITE,markersize=3)
    label(a,2.9,1.83,'AP / transmitter',12,weight='bold')
    # Receiver laptop.
    rect(a,8.2,2.32,1.15,.7,GREY,TEAL)
    a.add_patch(Polygon([(8.02,2.15),(9.53,2.15),(9.35,2.32),(8.2,2.32)],fc=TEAL))
    label(a,8.78,1.83,'STA / receiver',12,weight='bold')
    arrow(a,(3.7,2.58),(7.95,2.58),TEAL,width=2)
    for k in range(4): rect(a,4.4+k*.65,2.88,.6,.36,ORANGE if k==2 else BLUE,hatch='////' if k==2 else None)
    label(a,5.65,2.12,'One 80 MHz link',12,TEAL,weight='bold')
    label(a,5.65,3.71,'Exogenous narrowband interferer',12,ORANGE,weight='bold')
    arrow(a,(6.0,3.52),(6.0,3.25),ORANGE,style='--')
    a.plot([.15,9.85],[1.43,1.43],color=GREY,lw=1.3)
    items=[(.25,2.55,'Shared busy / clear trace\nFresh primary CCA + probes'),
           (3.57,2.5,'Select an allowed mask\nCharge time costs'),
           (6.83,2.93,'Record goodput, wait\nand unused clear MHz')]
    for x,w,t in items:
        rect(a,x,.3,w,.72,'#f1f5f8',OUTLINE)
        label(a,x+w/2,.66,t,11.4)
    arrow(a,(2.85,.66),(3.5,.66),INK)
    arrow(a,(6.13,.66),(6.76,.66),INK)
    save(f,root,'concept_system_topology')

def masks(root):
    f,a=setup(9.5,3.4)
    xs=[3.45,4.2,4.95,5.7]
    for x,t in zip(xs,['P','S1','S2','S3']):label(a,x+.3,3.12,t,13,weight='bold')
    rows=[('Full bandwidth','1111',80),('Puncture S1','1011',60),
          ('Puncture S2','1101',60),('Puncture S3','1110',60),
          ('20 MHz fallback','1000',20)]
    for j,(name,bits,bw) in enumerate(rows):
        y=2.6-j*.49
        label(a,.18,y+.16,name,12,ha='left',weight='bold' if j==4 else 'normal')
        label(a,2.75,y+.16,bits,12)
        for k,(x,b) in enumerate(zip(xs,bits)):
            rect(a,x,y,.62,.32,BLUE if b=='1' else GREY,OUTLINE,
                 hatch='///' if b=='0' and j<4 else None)
        label(a,6.95,y+.16,f'{bw} MHz',12,ha='left',weight='bold')
    label(a,9.15,2.0,'Primary\nalways\nactive',12,TEAL,weight='bold')
    a.plot([3.4,4.12],[.43,.43],color=TEAL,lw=2)
    a.plot([.15,7.85],[1.045,1.045],color=OUTLINE,lw=.7,ls='--')
    label(a,5.0,.14,'60 MHz rows are puncturing; 20 MHz is a separate narrower transmission',11.3)
    save(f,root,'concept_allowed_masks')

def airtime(root):
    f,a=setup(10,2.85)
    left=.65;width=8.7
    label(a,5,2.66,'Example frame: AgeAware changes to 20 MHz, with no scheduled probe',12.3,weight='bold')
    ctrl=.075
    rect(a,left,1.79,width*ctrl,.46,ORANGE,ORANGE)
    rect(a,left+width*ctrl,1.79,width*(1-ctrl),.46,BLUE,BLUE)
    label(a,5.6,2.02,'Payload time = 0.925 ms',13,WHITE,weight='bold')
    label(a,left,1.59,'0',11,ha='left'); label(a,left+width,1.59,'1 ms',11,ha='right')
    label(a,1.0,2.4,'Control',11.5,ORANGE)
    # Expand only the control portion, retaining exact relative widths below.
    a.plot([left,left],[1.77,1.21],color=OUTLINE,ls='--',lw=1)
    parts=[(.01,TEAL,'CCA\n0.010 ms'),(.04,'#b9c9d5','Signalling\n0.040 ms'),
           (.02,'#a7ced3','Switch\n0.020 ms'),(.005,RED,'Compute\n0.005 ms')]
    x=left
    for dt,col,name in parts:
        w=width*dt/ctrl;rect(a,x,.78,w,.39,col,col)
        label(a,x+w/2,.38,name,10.8)
        x+=w
    label(a,5,1.36,'Expanded control budget = 0.075 ms',11.5,ORANGE,weight='bold')
    save(f,root,'concept_airtime_budget')

def stale(root):
    f,a=setup(10,3.55)
    label(a,5,3.34,'Same old observation, different decision at age a = 2 frames',13,weight='bold')
    headers=['Last probe\n(a = 0)','True state now\n(a = 2)','Greedy\nuses 1111','AgeAware\nuses 1000']
    xs=[.35,2.85,5.35,7.85]
    for i,(x,title) in enumerate(zip(xs,headers)):
        label(a,x+.9,2.75,title,12.2,weight='bold')
        for k in range(4):
            if i==0:col=BLUE;h=None
            elif i==1:col=ORANGE if k==2 else BLUE;h='///' if k==2 else None
            elif i==2:col=RED if k==2 else BLUE;h='xxx' if k==2 else None
            else:col=BLUE if k==0 else GREY;h=None
            rect(a,x+k*.45,1.89,.41,.46,col,OUTLINE,hatch=h)
        label(a,x+.9,1.62,['All blocks clear','S2 becomes busy','Aggregate fails','Primary succeeds'][i],11.5,
              color=RED if i==2 else (TEAL if i==3 else INK))
    arrow(a,(2.24,2.13),(2.75,2.13),OUTLINE)
    arrow(a,(4.75,2.13),(5.24,2.13),OUTLINE)
    # Both policies use the probe at a=0; the true state is shown for explanation only.
    label(a,5,1.20,'Secondary states S1–S3 are unobserved between scheduled probes.',11.8,RED)
    label(a,5,.74,r'For each secondary: $q = 1 - 0.6 + 0.6(0.2)^2 = 0.424$',12.5,weight='bold')
    label(a,5,.25,'Primary P is verified clear in every frame via immediate CCA.',11.0,INK)
    save(f,root,'concept_stale_measurement')

def create(root):
    for fn in [spectrum,topology,masks,airtime,stale]:fn(root)
    manifest={
      'concept_puncturing':{'figure':'Figure 1','basis':'Adapted from [11]','description':'80 MHz channel with single secondary 20 MHz puncture (mask 1101)'},
      'concept_system_topology':{'figure':'Figure 2','basis':'Adapted from [12]','description':'Saturated AP-to-STA link topology and per-frame scheduling pipeline'},
      'concept_allowed_masks':{'figure':'Figure 3','basis':'Mask subset from [9,10], layout from [11]','description':'Four 80 MHz non-OFDMA patterns plus 20 MHz primary fallback'},
      'concept_airtime_budget':{'figure':'Figure 4','description':'1 ms frame airtime breakdown (0.075 ms control overhead, 0.925 ms payload)'},
      'concept_stale_measurement':{'figure':'Figure 9','description':'Decision comparison at probe age a=2 frames (d=0.6, rho=0.2)'}
    }
    (root/'results/illustration_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')

if __name__=='__main__':create(Path(__file__).resolve().parents[2])
