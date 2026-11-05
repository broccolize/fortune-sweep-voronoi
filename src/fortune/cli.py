"""Documented batch and interactive entry points."""

import argparse
import json
import sys
from .diagram import construct
from .geometry import Box
from .io import read_sites, random_sites, write_csv, write_json


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    parser = argparse.ArgumentParser(description='Fortune sweep-line Voronoi diagrams, from scratch.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--input',help='UTF-8 coordinate file: x y or x,y per line')
    group.add_argument('--random',type=int,metavar='N',help='N uniform sites in the unit square')
    parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--bbox',type=float,nargs=4,metavar=('XMIN','YMIN','XMAX','YMAX'))
    parser.add_argument('--output',help='PNG or SVG image path')
    parser.add_argument('--csv',help='Ordered cell boundaries and explicit clipped-edge records')
    parser.add_argument('--json',dest='json_path',help='Complete diagram including rays and defining triples')
    parser.add_argument('--interactive',action='store_true',help='Click-to-add interface')
    parser.add_argument('--show',action='store_true',help='Display batch output on screen')
    parser.add_argument('--no-labels',action='store_true',help='Hide indices for dense previews')
    args = parser.parse_args(argv)
    try:
        sites = read_sites(args.input) if args.input else random_sites(args.random,args.seed) if args.random is not None else []
        box = Box(*args.bbox) if args.bbox else Box(0,0,1,1) if args.random is not None else None
        if args.interactive or not argv:
            from .interactive import launch
            launch(sites,box,args.output or 'interactive.png')
            return 0
        if not sites:
            parser.error('Specify --input FILE, --random N, or --interactive')
        diagram = construct(sites,box)
        if args.csv:
            write_csv(diagram,args.csv)
        if args.json_path:
            write_json(diagram,args.json_path)
        if args.output or args.show:
            from .visualize import render
            render(diagram,args.output,show=args.show,labels=not args.no_labels)
        print(json.dumps(diagram.statistics,indent=2))
    except (ValueError,ArithmeticError,OSError) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        return 2
    return 0
