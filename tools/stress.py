"""Independent stress validation, including every 10,000-site circle vertex.

NumPy is used only as a validation utility to accelerate brute-force distance
scans. It is not imported by the Fortune construction engine.
"""
import argparse
import json
from pathlib import Path
import random
import sys
import time
import traceback
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')]
import numpy as np
from fortune import construct,Box
from validation import validate_cells,validate_empty_circles


def check_all_vertices(diagram):
    sites=np.array([(p.x,p.y) for p in diagram.sites])
    for vertex in diagram.vertices:
        distances=np.hypot(sites[:,0]-vertex.point.x,sites[:,1]-vertex.point.y)
        defining=distances[list(vertex.defining)]
        r=float(defining[0]);tol=1e-8*max(1,r)
        assert float(defining.max()-defining.min())<=tol,'equidistance'
        assert float(distances.min())>=r-tol,'nonempty circle'


def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=300)
    p.add_argument('--largest',type=int,default=10000);args=p.parse_args()
    started=time.perf_counter();failures=[];checked=0
    for seed in range(args.seeds):
        rng=random.Random(seed)
        d=construct([(rng.random(),rng.random()) for _ in range(10+seed%80)],Box(0,0,1,1))
        validate_cells(d,queries=25,seed=seed);validate_empty_circles(d);checked+=1
    # More than one cluster seed prevents a fortunate single example from
    # masquerading as a broad near-coincidence check.
    for exponent in (10,12):
        for seed in range(20):
            rng=random.Random(seed)
            points=[(0,0),(1,0),(1,1),(0,1)]+[
                (.4+10**-exponent*rng.random(),.6+10**-exponent*rng.random()) for _ in range(6)]
            try:
                d=construct(points,debug=True);validate_cells(d,queries=50,seed=seed)
                validate_empty_circles(d);checked+=1
            except Exception as exc:
                failures.append(dict(exponent=exponent,seed=seed,input=points,
                                     error=repr(exc),traceback=traceback.format_exc()))
    large=[]
    for n in (100,1000,args.largest):
        rng=random.Random(2026)
        d=construct([(rng.random(),rng.random()) for _ in range(n)],Box(0,0,1,1))
        validate_cells(d,queries=100,seed=2026);check_all_vertices(d)
        large.append(dict(n=n,vertices_checked=len(d.vertices),cell_queries=100))
    result=dict(status='passed' if not failures else 'failed',random_configurations=args.seeds,
                cluster_cases=40,checked_configurations=checked,queries_per_random=25,
                largest_cases=large,failures=failures,seconds=time.perf_counter()-started)
    (ROOT/'evidence'/'stress-final.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2));return bool(failures)


if __name__=='__main__':raise SystemExit(main())
