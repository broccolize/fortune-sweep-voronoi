"""Reproduce all original program and explanatory figures from recorded data."""

import json
import math
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'tmp'/'matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fortune import construct,Box
from fortune.geometry import Point,parabola_y
from fortune.io import read_sites,random_sites,write_csv,write_json
from fortune.visualize import draw,render

OUT=ROOT/'figures'


def main():
    OUT.mkdir(exist_ok=True)
    d=construct(read_sites(ROOT/'examples'/'sites.txt'),Box(0,0,1,1))
    render(d,OUT/'general.png')
    render(d,ROOT/'examples'/'general.svg')
    write_csv(d,ROOT/'examples'/'cells.csv');write_json(d,ROOT/'examples'/'diagram.json')
    large=construct(random_sites(1000,2026),Box(0,0,1,1))
    render(large,OUT/'large.png',labels=False)
    cases=[('Horizontal collinear',[(i,0) for i in range(5)]),
           ('Vertical collinear',[(0,i) for i in range(5)]),
           ('Slanted collinear',[(i,2*i) for i in range(5)]),
           ('Cocircular square',[(0,0),(1,0),(1,1),(0,1)]),
           ('Duplicate index groups',[(0,0),(1,0),(0,1),(0,0)]),
           ('Near sites 1e-11 apart',[(0,0),(1e-11,1e-11),(1,0),(.3,.7),(0,1)]),
           ('Single site',[(0,0)]),('Two sites',[(0,0),(1,1)])]
    for half in range(2):
        fig,axes=plt.subplots(2,2,figsize=(10,9))
        for ax,(title,points) in zip(axes.flat,cases[half*4:half*4+4]):
            draw(construct(points),ax)
            ax.set_title(title,fontsize=12)
        fig.tight_layout();fig.savefig(OUT/f'degenerate-{half+1}.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5))
    boxes=[(.02,.6,'Input and exact duplicates'),(.35,.6,'Fortune sweep\nAVL arcs and event heap'),(.69,.6,'Adjacency and traced edges'),
           (.35,.12,'Angle sorted half planes\nBox clipping and ordered cells'),(.71,.12,'CLI and Matplotlib\nCSV JSON PNG SVG')]
    for x,y,label in boxes:
        ax.add_patch(plt.Rectangle((x,y),.27,.22,facecolor='#e9eff9',edgecolor='#355070'))
        ax.text(x+.135,y+.11,label,ha='center',va='center',fontsize=11)
    for start,end in [((.29,.71),(.35,.71)),((.62,.71),(.69,.71)),((.82,.6),(.5,.34)),((.62,.23),(.71,.23))]:
        ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',lw=1.5))
    ax.text(.02,.07,'Independent tests validate output; no validator is used to build the diagram.',fontsize=10)
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');fig.tight_layout();fig.savefig(OUT/'architecture.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5))
    points=[Point(-.6,.8),Point(.2,.6),Point(.75,1.0)];ly=-.2
    xs=[-1.2+i*2.4/700 for i in range(701)]
    curves=[[parabola_y(p,x,ly) for x in xs] for p in points]
    for i,(p,ys) in enumerate(zip(points,curves)):
        ax.plot(xs,ys,alpha=.4);ax.scatter(p.x,p.y,c='black');ax.annotate(f'p{i}',(p.x,p.y),xytext=(5,5),textcoords='offset points')
    ax.plot(xs,[min(values) for values in zip(*curves)],lw=2.5,c='#1f4e79',label='Beach line lower envelope')
    ax.axhline(ly,c='#b42318',ls='--',label='Sweep directrix')
    ax.set(xlim=(-1.2,1.2),ylim=(-.4,1.5),xlabel='x',ylabel='y');ax.legend();fig.tight_layout();fig.savefig(OUT/'beachline.png',dpi=160);plt.close(fig)
    data=json.loads((ROOT/'results'/'benchmark.json').read_text())['results']
    ns=[row['n'] for row in data];ts=[row['median_seconds'] for row in data]
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    axes[0].loglog(ns,ts,'o-',label='Measured median, 3 runs')
    axes[0].loglog(ns,[ts[0]*n*math.log2(n)/(ns[0]*math.log2(ns[0])) for n in ns],'--',label='n log2 n, anchored at 100')
    axes[0].set(xlabel='Sites n',ylabel='Construction time (seconds)',title='Time scaling');axes[0].legend(fontsize=9)
    axes[1].loglog(ns,[r['python_peak_bytes']/2**20 for r in data],'o-',label='Traced Python peak')
    axes[1].loglog(ns,[r['process_peak_rss_bytes']/2**20 for r in data],'s-',label='Process peak with tracer')
    axes[1].set(xlabel='Sites n',ylabel='Peak memory (MiB)',title='Memory in isolated processes');axes[1].legend(fontsize=9)
    for ax in axes:ax.grid(True,which='both',alpha=.25)
    fig.tight_layout();fig.savefig(OUT/'scaling.png',dpi=180);plt.close(fig)
    print('Wrote original figures, SVG example, CSV and JSON exports')


if __name__=='__main__':main()
