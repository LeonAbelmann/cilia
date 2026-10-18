# run_batch.py
"""Run a batch of simulations from an experiment manifest.

Usage (command line):  python run_batch.py example_manifest.csv
                       python run_batch.py            (uses default below)
Usage (Jupyter):      from run_batch import run_batch
                       run_batch('example_manifest.csv')
"""
import os
import sys
import datetime
import numpy as np
from fields import FieldSequence
from rods import RodDescription
from simulator import simulate
from settings import DEFAULT as SETTINGS
from output import write_output

DEFAULT_MANIFEST = 'manifest.csv'


def load_manifest(filename):
    """Parse a manifest: '# key : value' header + rod_file,result_file rows."""
    meta, rows = {}, []
    with open(filename) as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if s.startswith('#'):
                text = s.lstrip('#').strip()
                if ':' in text:
                    key, value = text.split(':', 1)
                    meta[key.strip()] = value.strip()
                continue
            if s.startswith('rod_file'):
                continue                      # column header row
            parts = [p.strip() for p in s.split(',')]
            rows.append(parts)
    return meta, rows


def run_batch(manifest_file=DEFAULT_MANIFEST, settings=SETTINGS,
              skip_existing=False):
    """Run all simulations declared in the manifest."""
    meta, rows = load_manifest(manifest_file)
    field_file = meta.get('field file')
    if not field_file:
        raise ValueError(
            f"manifest {manifest_file} has no '# field file :' line")

    field = FieldSequence(field_file)

    for k, (rod_file, result_file) in enumerate(rows):
        print(f"[{k+1}/{len(rows)}] {rod_file} -> {result_file}")
        if skip_existing and os.path.exists(result_file):
            print(f"    exists, skipping (skip_existing=True)")
            continue
        if not skip_existing and os.path.exists(result_file):
            raise FileExistsError(
                f"{result_file} exists; refusing to overwrite. "
                "Delete it, edit the manifest, or use skip_existing=True")

        rod = RodDescription(rod_file)
        result = simulate(field, rod, settings=settings)
        write_output(result, field, rod, settings,
                     outfile=result_file,
                     program='run_batch.py',
                     manifest=manifest_file)
    print(f"Done: {len(rows)} simulations from {manifest_file}")


def main():
    # command line: optional manifest filename as first argument
    manifest = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MANIFEST
    run_batch(manifest)


if __name__ == '__main__':
    main()
