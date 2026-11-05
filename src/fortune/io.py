"""Coordinate parsing and explicit ordered-cell, clipped-edge exports."""

import csv
import json
import random
from pathlib import Path
from .geometry import Point


def read_sites(path):
    sites = []
    for number, line in enumerate(Path(path).read_text(encoding='utf-8-sig').splitlines(), 1):
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        fields = line.replace(',', ' ').split()
        if len(fields) != 2:
            raise ValueError(f'{path}, line {number}: expected exactly x y or x,y')
        try:
            sites.append(Point(float(fields[0]), float(fields[1])))
        except ValueError as exc:
            raise ValueError(f'{path}, line {number}: invalid number') from exc
    return sites


def random_sites(count, seed):
    if count < 1:
        raise ValueError('Random site count must be positive')
    rng = random.Random(seed)
    return [Point(rng.random(), rng.random()) for _ in range(count)]


def ensure_parent(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(diagram, path):
    edge_by_pair = {e.sites: e for e in diagram.edges}
    fields = ['cell', 'input_indices', 'site_x', 'site_y', 'unbounded_cell',
              'vertex_order', 'x', 'y', 'next_x', 'next_y', 'neighbour',
              'edge_kind', 'ray_origin_x', 'ray_origin_y', 'direction_x', 'direction_y']
    with ensure_parent(path).open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for c in diagram.cells:
            site = diagram.sites[c.site]
            base = dict(cell=c.site, input_indices=';'.join(map(str,c.input_indices)),
                        site_x=site.x, site_y=site.y, unbounded_cell=int(c.unbounded))
            if not c.vertices:
                writer.writerow(base | {'edge_kind':'empty_clipped_cell'})
            for k, p in enumerate(c.vertices):
                q = c.vertices[(k+1) % len(c.vertices)]
                j = c.boundary_neighbours[k]
                edge = edge_by_pair.get((min(c.site,j),max(c.site,j))) if j is not None else None
                row = base | dict(vertex_order=k, x=p.x, y=p.y, next_x=q.x, next_y=q.y,
                                  neighbour='' if j is None else j,
                                  edge_kind=edge.kind if edge else 'box')
                if edge and edge.origin:
                    row.update(ray_origin_x=edge.origin.x,ray_origin_y=edge.origin.y)
                if edge and edge.direction:
                    row.update(direction_x=edge.direction.x,direction_y=edge.direction.y)
                writer.writerow(row)


def write_json(diagram, path):
    def pair(p):
        return [p.x,p.y] if p is not None else None
    payload = dict(schema_version=1, bbox=diagram.box.as_tuple(),
                   sites=[pair(p) for p in diagram.sites], statistics=diagram.statistics,
                   cells=[dict(site=c.site, input_indices=c.input_indices,
                               unbounded=c.unbounded, vertices=[pair(p) for p in c.vertices],
                               boundary_neighbours=c.boundary_neighbours) for c in diagram.cells],
                   edges=[dict(sites=e.sites, start=pair(e.start),end=pair(e.end),
                               kind=e.kind, unbounded=e.unbounded,
                               origin=pair(e.origin),direction=pair(e.direction)) for e in diagram.edges],
                   vertices=[dict(point=pair(v.point),defining=sorted(v.defining)) for v in diagram.vertices])
    ensure_parent(path).write_text(json.dumps(payload,indent=2,allow_nan=False),encoding='utf-8')
