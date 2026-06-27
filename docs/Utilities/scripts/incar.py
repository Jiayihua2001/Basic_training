#!/usr/bin/env python3
"""
incar.py -- generate an INCAR file for the Marom-group VASP tutorials.

Usage examples
--------------
    python incar.py --scf                       # plain PBE SCF
    python incar.py --dos                       # DOS calculation
    python incar.py --band                      # band structure (PBE)
    python incar.py --opt                       # ionic relaxation
    python incar.py --scf  --soc                # PBE + SOC SCF (uses vasp_ncl)
    python incar.py --band --soc --hse          # HSE+SOC band
    python incar.py --scf  --dftu --ldaul 1 1 \
                                  --ldauu -0.5 -7.5     # DFT+U with effective U values

Defaults (always written; based on VASP-wiki recommendations)
-------------------------------------------------------------
  EDIFF        = 1E-8        # tighter than the VASP default 1E-4. The wiki
                             # notes 1E-6 as "the best compromise"; we go tighter, to
                             # 1E-8 for well-converged energies, forces, and restarts.
  GGA_COMPAT   = .False.     # restore full Bravais-lattice symmetry of the
                             # gradient field; default of .True. only exists
                             # for backward compatibility.
  ALGO         = Fast        # Davidson + RMM-DIIS for PBE; automatically
                             # switched to ALGO = All for HSE (--hse), which is
                             # the robust all-bands optimiser for hybrids.
  NBANDS       --            # NOT written. VASP's default
                             # max( (NELECT+2)/2 + max(NIONS/2, 3), 0.6*NELECT )
                             # is fine for the systems used in these tutorials;
                             # SOC doubles it internally.

The output is column-aligned: every "=" lines up, and every inline "#" comment
lines up, so the generated INCAR matches the blocks shown in the tutorials.
"""

import argparse
import os
import re
import textwrap


# Drop any tag that gets set more than once, keeping only the last occurrence.
# VASP uses last-wins semantics, but echoing the override on top of the
# original value clutters the INCAR (e.g. ALGO = All in the general block
# followed by ALGO = None in a HSE-DOS block).
_TAG_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=")


def _deduplicate_tags(text):
    lines = text.splitlines()
    occurrences = {}
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            continue
        m = _TAG_RE.match(line)
        if m:
            occurrences.setdefault(m.group(1).upper(), []).append(i)
    drop = {i for idxs in occurrences.values() if len(idxs) > 1 for i in idxs[:-1]}
    return "\n".join(line for i, line in enumerate(lines) if i not in drop)


# Align every "TAG = value  # comment" line: pad the tag so all "=" line up,
# pad the value so all inline "#" line up. Comment text is therefore left-
# aligned with respect to a single "#" column across the whole file.
_TAGLINE_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=(.*)$")


def _format_incar(text):
    parsed, tag_w, val_w = [], 0, 0
    for line in text.splitlines():
        m = _TAGLINE_RE.match(line)
        if m and not line.lstrip().startswith("#"):
            tag, rest = m.group(1), m.group(2)
            if "#" in rest:
                value, comment = rest.split("#", 1)
                value, comment = value.strip(), comment.strip()
            else:
                value, comment = rest.strip(), None
            parsed.append(("tag", tag, value, comment))
            tag_w = max(tag_w, len(tag))
            if comment is not None:
                val_w = max(val_w, len(value))
        else:
            parsed.append(("raw", line))

    out = []
    for item in parsed:
        if item[0] == "raw":
            out.append(item[1])
            continue
        _, tag, value, comment = item
        if comment is None:
            out.append(f"{tag:<{tag_w}} = {value}")
        else:
            out.append(f"{tag:<{tag_w}} = {value:<{val_w}}  # {comment}")
    return "\n".join(out)


# --- INCAR fragments ---------------------------------------------------------
# Written with single-space padding; _format_incar aligns them on output.
GENERAL = """\
# --- general ---
ALGO = {algo}  # {algo_comment}
PREC = Normal  # Precision level
EDIFF = {ediff}  # Electronic SC-loop break condition (eV); tight
NELM = 500  # Maximum number of electronic SCF steps
ENCUT = {encut}  # Plane-wave cutoff (eV)
LASPH = .True.  # Non-spherical contributions from gradient corrections
GGA_COMPAT = .False.  # Restore full lattice symmetry (recommended; required for MAE)
BMIX = 3  # Mixing parameter for convergence
AMIN = 0.01  # Mixing parameter for convergence
SIGMA = 0.05  # Smearing width (eV)

# --- parallelisation (Perlmutter CPU defaults) ---
KPAR = {kpar}  # k-points treated in parallel
NCORE = {ncore}  # Auto-reset to 1 by VASP under OpenMP/GPU
"""

SCF = """\
# --- SCF ---
ICHARG = 2  # Initial charge from atomic superposition
ISMEAR = 0  # Gaussian smearing for SCF
LCHARG = .True.  # Write CHG/CHGCAR for downstream PBE post-SCF (ICHARG = 11)
LWAVE = {lwave}  # {lwave_comment}
LREAL = .False.  # Reciprocal-space projectors (most accurate; fine for small cells)
"""

DOS = """\
# --- DOS ---
ICHARG = 11  # Read converged CHGCAR; non-SC eigenvalue calc
ISMEAR = -5  # Tetrahedron with Bloechl correction
LCHARG = .False.  # Do not write CHG/CHGCAR
LWAVE = .False.  # Do not write WAVECAR
LORBIT = 11  # lm-decomposed PROCAR / DOSCAR
NEDOS = 3001  # DOS sampling points
EMIN = emin  # Filled in by sbatch script from SCF Fermi level
EMAX = emax  # Filled in by sbatch script from SCF Fermi level
"""

# HSE DOS: ALGO = None just reads orbitals/eigenvalues from WAVECAR (VASP wiki:
# IALGO = 2). No Hamiltonian is evaluated, so no LHFCALC/HFSCREEN/AEXX needed.
# The DOS k-mesh therefore equals the SCF k-mesh (whatever WAVECAR holds).
DOS_HSE = """\
# --- DOS (post-process WAVECAR; HSE -- no Fock exchange evaluated) ---
ALGO = None  # Postprocess only: read orbitals + eigenvalues from WAVECAR
NELM = 1  # No iteration (paired with ALGO = None)
ISTART = 1  # Read WAVECAR
ICHARG = 0  # Required for hybrids (never use ICHARG = 11 with HSE)
ISMEAR = -5  # Tetrahedron with Bloechl correction
LCHARG = .False.  # Do not write CHG/CHGCAR
LWAVE = .False.  # Do not write WAVECAR
LORBIT = 11  # lm-decomposed PROCAR / DOSCAR
NEDOS = 3001  # DOS sampling points
EMIN = emin  # Filled in by sbatch script from SCF Fermi level
EMAX = emax  # Filled in by sbatch script from SCF Fermi level
"""

BAND = """\
# --- band ---
ICHARG = 11  # Read converged CHGCAR; non-SC band evaluation
ISMEAR = 0  # Gaussian smearing
LCHARG = .False.  # Do not write CHG/CHGCAR
LWAVE = .False.  # Do not write WAVECAR (.True. for unfolding)
LORBIT = 11  # lm-decomposed PROCAR
"""

# HSE band: KPOINTS file is SCF IBZKPT + line k-points with weight 0.
# ALGO = All (set in the general block) iterates over the new line k-points
# using the converged orbitals read from WAVECAR (ISTART = 1) as the starting
# guess. ICHARG = 11 is forbidden for hybrids.
BAND_HSE = """\
# --- band (HSE; restart from WAVECAR with zero-weight line k-points) ---
ISTART = 1  # Read WAVECAR
ICHARG = 0  # Required for hybrids; charge derived from orbitals
ISMEAR = 0  # Gaussian smearing
LCHARG = .False.  # Do not write CHG/CHGCAR
LWAVE = .False.  # Do not write WAVECAR (.True. for unfolding)
LORBIT = 11  # lm-decomposed PROCAR
"""

OPT = """\
# --- optimisation ---
ICHARG = 2  # Initial charge from atomic superposition
ISMEAR = 0  # Gaussian smearing
LCHARG = .False.  # Do not write CHG/CHGCAR
LWAVE = .False.  # Do not write WAVECAR
IBRION = 2  # Conjugate-gradient ionic relaxation
NSW = 50  # Maximum ionic steps
"""

SOC = """\
# --- spin-orbit coupling (use vasp_ncl) ---
LSORBIT = .True.  # Turn on spin-orbit coupling
MAGMOM = {magmom}  # 3 components (mx my mz) per atom
"""

DFTU = """\
# --- DFT+U (Dudarev) ---
LDAU = .True.  # Turn on DFT+U
LDAUTYPE = 2  # Dudarev formulation (only U_eff = U - J matters)
LDAUL = {ldaul}  # l-quantum number per species (-1 = off)
LDAUU = {ldauu}  # Effective U per species
LDAUJ = {ldauj}  # Always 0 for Dudarev
LMAXMIX = 4  # 4 for d electrons, 6 for f
"""

# HSE block: ALGO is set to All in the general block above, so it is NOT
# repeated here. TIME is the trial step used by the ALGO = All optimiser.
HSE = """\
# --- HSE06 hybrid functional ---
LHFCALC = .True.  # Turn on Hartree-Fock exchange
HFSCREEN = 0.2  # HSE06 range-separation parameter (1/Angstrom)
AEXX = 0.25  # Fraction of exact exchange (HSE06 standard)
PRECFOCK = Fast  # Reduced FFT mesh for the exchange routine
TIME = 0.4  # Trial time step for the ALGO = All band optimiser
"""


# --- driver ------------------------------------------------------------------
def build_incar(args):
    # HSE uses the robust all-bands optimiser; PBE uses Davidson + RMM-DIIS.
    if args.hse:
        algo, algo_comment = "All", "All-bands simultaneous update; robust for hybrids"
    else:
        algo, algo_comment = "Fast", "Mixture of Davidson + RMM-DIIS"

    parts = [GENERAL.format(
        algo=algo, algo_comment=algo_comment,
        ediff=args.ediff, encut=args.encut,
        kpar=args.kpar, ncore=args.ncore,
    )]

    # exactly one of {scf, dos, band, opt} is required
    main = next((s for s in ("scf", "dos", "band", "opt")
                 if getattr(args, s)), None)
    if main is None:
        raise SystemExit("Choose one of --scf / --dos / --band / --opt.")

    if args.scf:
        if args.hse:
            lwave = ".True."
            lwave_comment = "Write WAVECAR (HSE post-SCF DOS reads it via ALGO = None)"
        else:
            lwave = ".False."
            lwave_comment = "Skip WAVECAR (PBE post-SCF reads CHGCAR via ICHARG = 11)"
        parts.append(SCF.format(lwave=lwave, lwave_comment=lwave_comment))
    elif args.dos:
        parts.append(DOS_HSE if args.hse else DOS)
    elif args.band:
        parts.append(BAND_HSE if args.hse else BAND)
    elif args.opt:
        parts.append(OPT)

    if args.dftu:
        parts.append(DFTU.format(
            ldaul=" ".join(str(x) for x in args.ldaul),
            ldauu=" ".join(str(x) for x in args.ldauu),
            ldauj=" ".join("0.0" for _ in args.ldaul),
        ))

    if args.soc:
        # default: zero MAGMOM; user supplies "0 0 0 0 0 0" or similar
        magmom = args.magmom or _default_magmom(args.poscar)
        parts.append(SOC.format(magmom=magmom))

    if args.hse:
        # SCF and band evaluate the HF exchange operator and need the HSE block.
        # DOS uses ALGO = None (no Hamiltonian eval), so HSE tags are unnecessary.
        if not args.dos:
            parts.append(HSE)
    elif main in ("scf", "opt") and not (args.soc or args.dftu):
        parts.append("# (Pure PBE; add --hse for HSE06 or --dftu for DFT+U)\n")

    return _format_incar(_deduplicate_tags("\n".join(parts)))


def _default_magmom(poscar_path):
    """Build MAGMOM = 'N*0' from a POSCAR (3 components per atom)."""
    if not os.path.isfile(poscar_path):
        return "0 0 0"
    with open(poscar_path) as fh:
        lines = fh.readlines()
    try:
        counts = [int(x) for x in lines[6].split()]
    except (IndexError, ValueError):
        # POSCAR has element labels on line 6 -> counts on line 7
        counts = [int(x) for x in lines[7].split()]
    n_atoms = sum(counts)
    return f"{3 * n_atoms}*0"


def parse_args():
    p = argparse.ArgumentParser(
        description=textwrap.dedent(__doc__),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    g = p.add_argument_group("calculation type (choose one)")
    g.add_argument("-s", "--scf",  action="store_true")
    g.add_argument("-d", "--dos",  action="store_true")
    g.add_argument("-b", "--band", action="store_true")
    g.add_argument("-o", "--opt",  action="store_true")

    m = p.add_argument_group("modifiers (combine with the above)")
    m.add_argument("-c", "--soc",  action="store_true",
                   help="Add spin-orbit (use vasp_ncl).")
    m.add_argument("-e", "--hse",  action="store_true",
                   help="Add HSE06 hybrid block (also sets ALGO = All).")
    m.add_argument("-u", "--dftu", action="store_true",
                   help="Add Dudarev DFT+U block.")

    p.add_argument("--ediff", default="1E-8",
                   help="EDIFF (default 1E-8; tight electronic convergence).")
    p.add_argument("--encut", type=int, default=400,
                   help="ENCUT in eV (default 400).")
    p.add_argument("--kpar",  type=int, default=4,
                   help="KPAR (default 4 for 16 MPI ranks/node CPU or 4 GPUs).")
    p.add_argument("--ncore", type=int, default=1,
                   help="NCORE (default 1; auto-reset to 1 by OpenMP / GPU anyway).")
    p.add_argument("--ldaul", type=int, nargs="+",
                   help="LDAUL list, one per species.")
    p.add_argument("--ldauu", type=float, nargs="+",
                   help="LDAUU list, one per species.")
    p.add_argument("--magmom", type=str,
                   help="MAGMOM string, e.g. '6*0' or '0 0 2.5 0 0 -2.5'.")
    p.add_argument("--poscar", default="POSCAR",
                   help="POSCAR used to count atoms for MAGMOM defaults.")
    p.add_argument("--output", default="INCAR",
                   help="Output filename (default INCAR).")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    text = build_incar(args)
    with open(args.output, "w") as fh:
        fh.write(text + "\n")
    print(f"Wrote {args.output} ({len(text.splitlines())} lines).")
