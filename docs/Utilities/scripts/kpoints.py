#!/usr/bin/env python3
"""
kpoints.py -- generate KPOINTS files for the VASP tutorials.

Three modes
-----------
1. Regular Monkhorst-Pack / Gamma-centred grid (SCF, DOS, OPT):
       python kpoints.py --grid -d 7 7 7

2. Line-mode k-path along high-symmetry points (PBE band):
       python kpoints.py --band -c GXWLGK -n 50

3. Hybrid (HSE) band structure -- combines an IBZKPT mesh with a
   zero-weighted line-mode path:
       python kpoints.py --band --hse -c GXWLGK -n 40 \
                                            --ibzkpt ../scf/IBZKPT

The high-symmetry path is generated with pymatgen's HighSymmKpath
(Setyawan-Curtarolo convention). For 1D/2D systems and quick INCAR
templates you may also prefer VASPKIT's options 102/251/302/303 which
are documented in the Utilities page.
"""

import argparse
import os
import warnings

import numpy as np
from pymatgen.core import Structure
from pymatgen.io.vasp.inputs import Kpoints
from pymatgen.symmetry.bandstructure import HighSymmKpath


def parse_args():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("-g", "--grid", action="store_true",
                      help="Write a Gamma-centred MP grid.")
    mode.add_argument("-b", "--band", action="store_true",
                      help="Write a line-mode (or HSE) k-path.")
    mode.add_argument("-l", "--list", action="store_true",
                      help="Print all high-symmetry labels for the POSCAR.")

    p.add_argument("-d", "--density", type=int, nargs=3, default=[7, 7, 7],
                   help="Grid density nx ny nz (default 7 7 7).")
    p.add_argument("-c", "--coords", type=str,
                   help="High-symmetry path, e.g. GXWLGK.")
    p.add_argument("-n", "--segments", type=int, default=50,
                   help="Number of k-points per segment (default 50).")
    p.add_argument("-e", "--hse", action="store_true",
                   help="Write KPOINTS for an HSE band (zero-weight scheme).")
    p.add_argument("-i", "--ibzkpt", default="IBZKPT",
                   help="IBZKPT file from the converged SCF run (HSE only).")
    p.add_argument("-p", "--poscar", default="POSCAR",
                   help="POSCAR file for symmetry analysis.")
    p.add_argument("-o", "--output", default="KPOINTS",
                   help="Output filename (default KPOINTS).")
    return p.parse_args()


def get_kpath(poscar, coords, segments):
    if not os.path.isfile(poscar):
        raise SystemExit(f"POSCAR not found at {poscar}.")
    structure = Structure.from_file(poscar)
    hsk = HighSymmKpath(structure, path_type="setyawan_curtarolo")
    kpoints = Kpoints.automatic_linemode(segments, hsk)
    kpoints.labels = [lab.replace("\\Gamma", "G") for lab in kpoints.labels]

    if coords:
        coords = coords.upper()
        if not all(c in kpoints.labels for c in coords):
            warnings.warn(
                f"Some labels in {coords} not found; available: "
                f"{sorted(set(kpoints.labels))}")
            return kpoints

        path = list(coords)
        # duplicate intermediate points: G X X W W L L G G K
        for i in reversed(range(1, len(path) - 1)):
            path.insert(i + 1, path[i])
        info = dict(zip(kpoints.labels, kpoints.kpts))
        kpoints.labels = path
        kpoints.kpts = [info[lab] for lab in path]
    return kpoints


def write_grid(density, output):
    nx, ny, nz = density
    with open(output, "w") as fh:
        fh.write("Automatic kpoint scheme\n0\nGamma\n"
                 f"{nx} {ny} {nz}\n")


def write_band(kpoints, output):
    with open(output, "w") as fh:
        fh.write(str(kpoints))


def write_hse_band(kpoints, ibzkpt_path, output):
    if not os.path.isfile(ibzkpt_path):
        raise SystemExit(f"IBZKPT not found at {ibzkpt_path}.")
    with open(ibzkpt_path) as fh:
        ibz_lines = fh.read().rstrip("\n").splitlines()
    n_ibz = int(ibz_lines[1].strip())

    # interpolate each (start,end) segment of the line-mode path
    pts_per_seg = kpoints.num_kpts
    kpts = kpoints.kpts
    interp = []
    for i in range(0, len(kpts) - 1, 2):
        a, b = np.array(kpts[i]), np.array(kpts[i + 1])
        for t in np.linspace(0.0, 1.0, pts_per_seg):
            interp.append((1 - t) * a + t * b)
    interp = np.array(interp)

    n_total = n_ibz + interp.shape[0]
    ibz_lines[1] = f"\t{n_total}"
    band_lines = [
        "  ".join(f"{x:.14f}" for x in pt) + "             0"
        for pt in interp
    ]

    with open(output, "w") as fh:
        fh.write("\n".join(ibz_lines) + "\n")
        fh.write("\n".join(band_lines) + "\n")


def main():
    args = parse_args()
    if args.grid:
        write_grid(args.density, args.output)
        return

    kpoints = get_kpath(args.poscar, args.coords, args.segments)

    if args.list:
        for lab, k in zip(kpoints.labels, kpoints.kpts):
            print(f"{lab:>4} -> [{', '.join(f'{x:.3f}' for x in k)}]")
        return

    if args.band and args.hse:
        write_hse_band(kpoints, args.ibzkpt, args.output)
    elif args.band:
        write_band(kpoints, args.output)


if __name__ == "__main__":
    main()
