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
  EDIFF        = 1E-6        # tighter than the VASP default 1E-4. The wiki
                             # notes that 1E-6 is "the best compromise" between
                             # accuracy and cost for production calculations.
  GGA_COMPAT   = .False.     # restore full Bravais-lattice symmetry of the
                             # gradient field; default of .True. only exists
                             # for backward compatibility.
  NBANDS       --            # NOT written. VASP's default
                             # max( (NELECT+2)/2 + max(NIONS/2, 3), 0.6*NELECT )
                             # is fine for the systems used in these tutorials;
                             # SOC doubles it internally.
"""

import argparse
import os
import textwrap


# --- INCAR fragments ---------------------------------------------------------
GENERAL = """\
# --- general -----------------------------------------------------------------
ALGO       = Fast        # Mixture of Davidson + RMM-DIIS
PREC       = Normal      # Precision level
EDIFF      = {ediff}     # Electronic SC break condition (VASP-wiki: 1E-6 is the best compromise)
NELM       = 500         # Maximum number of electronic SCF steps
ENCUT      = {encut}     # Plane-wave cutoff (eV)
LASPH      = .True.      # Non-spherical contributions from gradient corrections
GGA_COMPAT = .False.     # Restore full lattice symmetry (recommended; required for MAE)
BMIX       = 3           # Mixing parameter for convergence
AMIN       = 0.01        # Mixing parameter for convergence
SIGMA      = 0.05        # Smearing width (eV)

# --- parallelisation (Perlmutter 1-node CPU defaults) ------------------------
KPAR       = {kpar}      # k-point parallelism
NCORE      = {ncore}     # MPI ranks collaborating on one band; ~sqrt(ranks per k-group)
"""

SCF = """\
# --- SCF ---------------------------------------------------------------------
ICHARG = 2               # Initial charge from atomic superposition
ISMEAR = 0               # Gaussian smearing for SCF
LCHARG = .True.          # Write CHG/CHGCAR for downstream PBE post-SCF (ICHARG = 11)
LWAVE  = {lwave}         # {lwave_comment}
LREAL  = Auto            # Automatically chooses real/reciprocal projections
"""

DOS = """\
# --- DOS ---------------------------------------------------------------------
ICHARG = 11              # Read converged CHGCAR; non-SC eigenvalue calc
ISMEAR = -5              # Tetrahedron with Bloechl correction
LCHARG = .False.
LWAVE  = .False.
LORBIT = 11              # lm-decomposed PROCAR / DOSCAR
NEDOS  = 3001
EMIN   = emin            # Filled in by sbatch script from SCF Fermi level
EMAX   = emax
"""

# HSE DOS: ALGO = None just reads orbitals/eigenvalues from WAVECAR (VASP wiki:
# IALGO = 2). No Hamiltonian is evaluated, so no LHFCALC/HFSCREEN/AEXX needed.
# The DOS k-mesh therefore equals the SCF k-mesh (whatever WAVECAR holds).
DOS_HSE = """\
# --- DOS (post-process WAVECAR; HSE) ----------------------------------------
ALGO   = None            # Postprocess only: read orbitals + eigenvalues from WAVECAR
NELM   = 1               # No iteration (paired with ALGO = None)
ISTART = 1               # Read WAVECAR
ICHARG = 0               # Required for hybrids (never use ICHARG = 11 with HSE)
ISMEAR = -5              # Tetrahedron with Bloechl correction
LCHARG = .False.
LWAVE  = .False.
LORBIT = 11              # lm-decomposed PROCAR / DOSCAR
NEDOS  = 3001
EMIN   = emin            # Filled in by sbatch script from SCF Fermi level
EMAX   = emax
"""

BAND = """\
# --- band --------------------------------------------------------------------
ICHARG = 11              # Read converged CHGCAR; non-SC band evaluation
ISMEAR = 0               # Gaussian smearing
LCHARG = .False.
LWAVE  = .False.
LORBIT = 11              # lm-decomposed PROCAR
"""

# HSE band: KPOINTS file is SCF IBZKPT + line k-points with weight 0.
# ALGO = Fast iterates over the new line k-points using the converged orbitals
# at the SCF k-points (read via ISTART = 1) as starting guess. ICHARG = 11
# is forbidden for hybrids.
BAND_HSE = """\
# --- band (HSE; restart from WAVECAR with zero-weight line k-points) ---------
ISTART = 1               # Read WAVECAR
ICHARG = 0               # Required for hybrids; charge derived from orbitals
ISMEAR = 0               # Gaussian smearing
LCHARG = .False.
LWAVE  = .False.
LORBIT = 11              # lm-decomposed PROCAR
"""

OPT = """\
# --- optimisation ------------------------------------------------------------
ICHARG = 2
ISMEAR = 0
LCHARG = .False.
LWAVE  = .False.
IBRION = 2               # Conjugate-gradient ionic relaxation
NSW    = 50              # Maximum ionic steps
"""

SOC = """\
# --- spin-orbit coupling -----------------------------------------------------
LSORBIT = .True.         # Use vasp_ncl for this calculation
MAGMOM  = {magmom}       # 3 components per atom
"""

DFTU = """\
# --- DFT+U (Dudarev simplified) ---------------------------------------------
LDAU     = .True.
LDAUTYPE = 2             # Dudarev formulation (only U_eff = U - J matters)
LDAUL    = {ldaul}       # l-quantum number per species (-1 = off)
LDAUU    = {ldauu}       # Effective U per species
LDAUJ    = {ldauj}
LMAXMIX  = 4             # 4 for d, 6 for f
"""

HSE = """\
# --- HSE06 hybrid functional -------------------------------------------------
LHFCALC  = .True.        # Turn on Hartree-Fock exchange
HFSCREEN = 0.2           # HSE06 range-separation parameter (1/A)
AEXX     = 0.25          # Fraction of exact exchange (HSE06 standard)
PRECFOCK = Fast          # Reduced FFT mesh for the exchange routine
TIME     = 0.4           # Damping time-step for ALGO = Damped
"""


# --- driver ------------------------------------------------------------------
def build_incar(args):
    parts = [GENERAL.format(
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
        if args.dos:
            pass
        else:
            parts.append(HSE)
    elif main in ("scf", "opt"):
        parts.append("# (Pure PBE; add --hse for HSE06 or --dftu for DFT+U)\n")

    return "\n".join(parts)


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
                   help="Add HSE06 hybrid block.")
    m.add_argument("-u", "--dftu", action="store_true",
                   help="Add Dudarev DFT+U block.")

    p.add_argument("--ediff", default="1E-6",
                   help="EDIFF (default 1E-6, see VASP wiki).")
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
        fh.write(text)
    print(f"Wrote {args.output} ({len(text.splitlines())} lines).")
