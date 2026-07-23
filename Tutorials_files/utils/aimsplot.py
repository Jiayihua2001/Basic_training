#!/usr/bin/env python3
"""
aimsplot.py - Plot band structure and DOS from an FHI-aims run.

Usage
-----
    python aimsplot.py                  # default y-range, legend on the right
    python aimsplot.py --Emin -15 --Emax 10 --no-legend
    python aimsplot.py --help           # full list of CLI flags

Requirements
------------
* numpy
* matplotlib

Input files expected in CWD:
    geometry.in
    control.in
    band{spin}{idx:03d}.out
    KS_DOS_total(_tetrahedron).dat
    <element>_l_proj_dos(_tetrahedron)[_spin_up/_spin_dn].dat
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import argparse
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------#
# Configuration knobs (all in one place)                                        #
# -----------------------------------------------------------------------------#
CONFIG = {
    "dpi": 300,
    "line_width": 1.25,          # plain-band linewidth (vaspvis convention)
    "font_size": 12,
    "default_ylim": (-6.0, 6.0),  # focus on the gap region; --Emin/--Emax to widen
    "spline_factor": 10,         # only used if --spline passed
}

mpl.rcParams["lines.linewidth"] = CONFIG["line_width"]
mpl.rcParams["savefig.dpi"] = CONFIG["dpi"]
mpl.rcParams["font.size"] = CONFIG["font_size"]
# publication-style axes: full box, inward ticks on all sides, minor ticks
mpl.rcParams.update({
    "axes.linewidth": 0.8,
    "xtick.direction": "in", "ytick.direction": "in",
    "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "xtick.major.size": 3.5, "ytick.major.size": 3.5,
    "xtick.minor.size": 2.0, "ytick.minor.size": 2.0,
    "legend.frameon": False,
    "legend.handlelength": 1.0,   # short line samples so the legend stays compact
    "legend.handletextpad": 0.4,
    "legend.borderaxespad": 0.3,
})


# -----------------------------------------------------------------------------#
# CLI options                                                                  #
# -----------------------------------------------------------------------------#
@dataclass
class Options:
    E_min: float
    E_max: float
    E_offset: float
    legend_x: float
    legend_y: float
    show_legend: bool
    show_l: bool
    spline: bool
    reverse_dos: bool = False  # set later based on what is plotted


def parse_args() -> Options:
    ap = argparse.ArgumentParser(description="Plot FHI-aims band structure and DOS")
    ap.add_argument("--Emin", type=float, default=None, help="Lower energy limit (eV)")
    ap.add_argument("--Emax", type=float, default=None, help="Upper energy limit (eV)")
    ap.add_argument("--Eoffset", type=float, default=0.0, help="Shift energies by this amount (eV)")
    ap.add_argument("--legend_x", type=float, default=1.5, help="Legend X position (axes fraction)")
    ap.add_argument("--legend_y", type=float, default=1.0, help="Legend Y position (axes fraction)")
    ap.add_argument("--no-legend", action="store_true", help="Suppress legend")
    ap.add_argument("--show_l_components", action="store_true", help="Plot l-resolved DOS where available")
    ap.add_argument("--spline", action="store_true", help="Spline-interpolate bands (experimental)")

    ns = ap.parse_args()

    return Options(
        E_min=ns.Emin if ns.Emin is not None else CONFIG["default_ylim"][0],
        E_max=ns.Emax if ns.Emax is not None else CONFIG["default_ylim"][1],
        E_offset=ns.Eoffset,
        legend_x=ns.legend_x,
        legend_y=ns.legend_y,
        show_legend=not ns.no_legend,
        show_l=ns.show_l_components,
        spline=ns.spline,
    )


# -----------------------------------------------------------------------------#
# Utility functions                                                            #
# -----------------------------------------------------------------------------#
def read_lattice_vectors(path: Path = Path("geometry.in")) -> np.ndarray:
    if not path.exists():
        sys.exit(f" geometry.in not found in {path.parent.resolve()}")
    latvec: List[np.ndarray] = []
    for line in path.read_text().splitlines():
        words = line.split("#")[0].split()
        if words[:1] == ["lattice_vector"]:
            if len(words) != 4:
                sys.exit(f"Syntax error in geometry.in line:\n{line}")
            latvec.append(np.asarray(list(map(float, words[1:4]))))
    if len(latvec) != 3:
        sys.exit("geometry.in must contain exactly three lattice_vector lines.")
    return np.vstack(latvec)  # (3,3)


def reciprocal_lattice(latvec: np.ndarray) -> np.ndarray:
    vol = np.dot(latvec[0], np.cross(latvec[1], latvec[2]))
    return 2 * np.pi * np.cross(latvec[[1, 2, 0]], latvec[[2, 0, 1]]) / vol


def parse_control() -> Tuple[dict, List[str]]:
    """Return dict with plot flags and list of species."""
    ctrl = Path("control.in")
    if not ctrl.exists():
        sys.exit(" control.in not found.")
    flags = {
        "bands": False,
        "dos": False,
        "dos_tetra": False,
        "species_dos": False,
        "species_dos_tetra": False,
        "soc": False,
        "max_spin": 1,
        "band_segments": [],  # each: (start,end,npts,start_lbl,end_lbl)
    }
    species: List[str] = []

    for raw in ctrl.read_text().splitlines():
        words = raw.split("#")[0].split()
        if not words:
            continue
        line = " ".join(words)

        if line.startswith("spin collinear"):
            flags["max_spin"] = 2
        if any(line.startswith(key) for key in (
            "calculate_perturbative_soc", "include_spin_orbit", "include_spin_orbit_sc"
        )):
            flags["soc"] = True
            flags["max_spin"] = 1

        if line.startswith("output band "):
            *vecs, npts = list(map(float, words[2:8])) + [int(words[8])]
            start, end = vecs[:3], vecs[3:]
            labels = words[9:11] if len(words) > 9 else ["", ""]
            flags["band_segments"].append((start, end, npts, *labels))
            flags["bands"] = True

        elif line.startswith("output dos_tetrahedron"):
            flags["dos_tetra"] = True
        elif line.startswith("output dos "):
            flags["dos"] = True
        elif line.startswith("output species_proj_dos_tetrahedron"):
            flags["species_dos_tetra"] = True
        elif line.startswith("output species_proj_dos "):
            flags["species_dos"] = True

        elif line.startswith("species"):
            if len(words) != 2:
                sys.exit(f"Syntax error in control.in line:\n{raw}")
            species.append(words[1])

    return flags, species


def load_band_file(spin: int, seg_idx: int, npts: int) -> Tuple[np.ndarray, np.ndarray]:
    fname = Path(f"band{spin}{seg_idx:03d}.out")
    if not fname.exists():
        sys.exit(f"Missing band file: {fname}")
    data = np.loadtxt(fname)
    kvec = data[:, 1:4]
    energies = data[:, 5::2]  # columns: idx kx ky kz occ1 e1 occ2 e2 ...
    if len(kvec) != npts:
        sys.exit(f"{fname} has {len(kvec)} points, expected {npts}")
    return kvec, energies


def spline_band(x: np.ndarray, y: np.ndarray, factor: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return smoothed x, y arrays. Cheap cubic spline via np.interp for now."""
    from scipy.interpolate import CubicSpline  # local import -> optional dependency
    x_smooth = np.linspace(x.min(), x.max(), factor * len(x))
    y_smooth = np.vstack([CubicSpline(x, y[:, i])(x_smooth) for i in range(y.shape[1])]).T
    return x_smooth, y_smooth


# -----------------------------------------------------------------------------#
# Plotting routines                                                            #
# -----------------------------------------------------------------------------#
def plot_bands(ax: plt.Axes, opts: Options, flags: dict, rlat: np.ndarray) -> None:
    segments = flags["band_segments"]
    if not segments:
        return
    distance = 0.03  # gap between disconnected segments (in units of total length)
    xpos = 0.0
    # seed with the FIRST segment's start label (e.g. the L in L-Gamma-X-W-K)
    labels_pos, labels_txt = [0.0], [segments[0][3]]

    for idx, (start, end, npts, lbl_start, lbl_end) in enumerate(segments, 1):
        # insert small horizontal gap if segment disjoint
        if idx > 1 and start != segments[idx - 2][1]:
            xpos += distance
            labels_pos.append(xpos)
            labels_txt.append(lbl_start)

        # absolute k-length of segment
        dk = np.linalg.norm(rlat @ (np.asarray(end) - np.asarray(start)))
        x = xpos + np.linspace(0, dk, npts)
        xpos = x[-1]
        labels_pos.append(xpos)
        labels_txt.append(lbl_end)

        for spin in range(1, flags["max_spin"] + 1):
            kvec, E = load_band_file(spin, idx, npts)
            E -= opts.E_offset
            if opts.spline:
                x_, E_ = spline_band(x, E, CONFIG["spline_factor"])
            else:
                x_, E_ = x, E
            # vaspvis conventions: plain bands black; spin-up red solid,
            # spin-down blue dotted
            if flags["max_spin"] == 2:
                color, ls, lw = (("red", "-", 1.1) if spin == 1
                                 else ("blue", ":", 1.1))
            else:
                color, ls, lw = "black", "-", CONFIG["line_width"]
            # label the spin channels once so a legend is meaningful
            lbl = None
            if flags["max_spin"] == 2 and idx == 1:
                lbl = r"$\uparrow$" if spin == 1 else r"$\downarrow$"
            lines = ax.plot(x_, E_, color=color, ls=ls, lw=lw, zorder=2)
            if lbl:
                lines[0].set_label(lbl)

    # vertical guides at high-symmetry points + Fermi-level guide
    for xp in labels_pos:
        ax.axvline(xp, color="black", alpha=0.7, linewidth=0.5, zorder=1)
    ax.axhline(0.0, color="gray", ls="--", linewidth=0.6, alpha=0.8, zorder=1)
    ax.set_xticks(labels_pos)
    # high-symmetry labels are upright (roman), not math italic
    ax.set_xticklabels([r"$\Gamma$" if t == "Gamma" else rf"$\mathrm{{{t}}}$"
                        for t in labels_txt])
    ax.set_xlim(0.0, xpos)
    ax.tick_params(axis="x", which="both", length=0)  # labels only on k axis

    ax.set_ylabel(r"$E - E_\mathrm{F}$ (eV)")
    ax.set_ylim(opts.E_min, opts.E_max)
    if opts.show_legend and ax.get_legend_handles_labels()[1]:
        ax.legend(loc="upper right", fontsize=10)


def plot_dos(ax: plt.Axes, opts: Options, flags: dict, species: List[str]) -> None:
    """Minimal total/species DOS plotting (tetrahedron aware)."""
    def read_total(tetra: bool) -> Tuple[np.ndarray, np.ndarray]:
        fname = Path("KS_DOS_total" + ("_tetrahedron" if tetra else "") + ".dat")
        if not fname.exists():
            sys.exit(f"Missing DOS file: {fname}")
        data = np.loadtxt(fname, comments="#")
        E = data[:, 0] - opts.E_offset
        D = data[:, 1:]  # 1 col (no spin) or 2 cols (collinear spin)
        return E, D

    E, D = read_total(flags["dos_tetra"])
    spinsgn = np.array([1, -1])[:D.shape[1]]  # [1] or [1,-1]

    # vaspvis-style: filled curves; spin-up red solid, spin-down blue dotted
    spin_lbl = [r"$\uparrow$", r"$\downarrow$"]
    two = D.shape[1] == 2
    colors = ("red", "blue") if two else ("black",)
    styles = ("-", ":") if two else ("-",)
    if opts.reverse_dos:
        for i in range(D.shape[1]):
            d = D[:, i] * spinsgn[i]
            ax.plot(d, E, color=colors[i], ls=styles[i], lw=1.0,
                    label=spin_lbl[i] if two else None, zorder=2)
            ax.fill_betweenx(E, 0, d, color=colors[i], alpha=0.15, lw=0)
        if two:
            ax.set_xlim(-1.05 * D.max(), 1.05 * D.max())
            ax.axvline(0, color="black", linewidth=0.5, alpha=0.7, zorder=1)
        else:
            ax.set_xlim(0, 1.05 * D.max())
        ax.set_xlabel("DOS (states/eV)", fontsize=10)
        ax.axhline(0, color="gray", ls="--", linewidth=0.6, alpha=0.8, zorder=1)
        # prune the lowest tick label so it can't collide with the band
        # panel's last k-point label at the shared boundary
        ax.xaxis.set_major_locator(mpl.ticker.MaxNLocator(3, prune="lower"))
    else:
        for i in range(D.shape[1]):
            d = D[:, i] * spinsgn[i]
            ax.plot(E, d, color=colors[i], ls=styles[i], lw=1.0,
                    label=spin_lbl[i] if two else None, zorder=2)
            ax.fill_between(E, 0, d, color=colors[i], alpha=0.15, lw=0)
        if two:
            ax.set_ylim(-1.05 * D.max(), 1.05 * D.max())
            ax.axhline(0, color="black", linewidth=0.5, alpha=0.7, zorder=1)
        else:
            ax.set_ylim(0, 1.05 * D.max())
        ax.set_xlabel(r"$E - E_\mathrm{F}$ (eV)")
        ax.set_ylabel("DOS (states/eV)")
        ax.axvline(0, color="gray", ls="--", linewidth=0.6, alpha=0.8, zorder=1)

    # only draw a legend when something is actually labeled (spin-polarized);
    # an unconditional call draws an empty box
    if opts.show_legend and ax.get_legend_handles_labels()[1]:
        ax.legend(loc="upper right", fontsize=10)


# -----------------------------------------------------------------------------#
# Main driver                                                                  #
# -----------------------------------------------------------------------------#
def main() -> None:
    opts = parse_args()
    latvec = read_lattice_vectors()
    rlat = reciprocal_lattice(latvec)

    flags, species = parse_control()

    # Decide subplot layout --------------------------------------------
    fig = plt.figure(figsize=(7.0, 4.6))
    if flags["bands"] and (flags["dos"] or flags["dos_tetra"]):
        gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.06)
        ax_bands = fig.add_subplot(gs[0, 0])
        ax_dos = fig.add_subplot(gs[0, 1], sharey=ax_bands)
        ax_dos.tick_params(labelleft=False)  # y labels belong to the band panel
        opts.reverse_dos = True
    elif flags["bands"]:
        ax_bands = fig.add_subplot(1, 1, 1)
        ax_dos = None
    else:
        ax_bands = None
        ax_dos = fig.add_subplot(1, 1, 1)

    # Plot --------------------------------------------------------------
    if ax_bands:
        plot_bands(ax_bands, opts, flags, rlat)
    if ax_dos:
        plot_dos(ax_dos, opts, flags, species)

    fig.tight_layout()
    fig.savefig("aimsplot.png", bbox_inches="tight")
    print("Plot saved to aimsplot.png (dpi =", CONFIG["dpi"], ")")
    plt.show()


if __name__ == "__main__":
    main()
