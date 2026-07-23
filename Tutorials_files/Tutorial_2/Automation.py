# make_k_grid.py
import numpy as np
import os
import matplotlib.pyplot as plt
import argparse
from ase.build import bulk
from ase.io import read,write
def make_k_grid(k_grid_min, k_grid_max):
    cp = os.getcwd()
    for k in range(k_grid_min, k_grid_max+1):
        if os.path.exists(f"{cp}/{k}"):
            continue
        os.makedirs(f"{cp}/{k}")
        if not os.path.exists(f"submit.sh"):
            raise FileNotFoundError(f"submit.sh not found in {cp}")
        if not os.path.exists(f"control.in"):
            raise FileNotFoundError(f"control.in not found in {cp}")
        if not os.path.exists(f"geometry.in"):
            raise FileNotFoundError(f"geometry.in not found in {cp}")
        os.system(f"cp submit.sh {cp}/{k}/submit.sh")
        os.system(f"cp control.in {cp}/{k}/control.in")
        os.system(f"cp geometry.in {cp}/{k}/geometry.in")
        # modify the control.in
        with open(f"{cp}/{k}/control.in", "r+") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "hessian_to_restart_geometry" in line:
                    insert_line = f"k_grid  {k} {k} {k}\n"
                    lines.insert(i + 1, insert_line)
            f.seek(0)
            f.writelines(lines)
            f.truncate()
        os.chdir(f"{cp}/{k}")
        os.system(f"sbatch submit.sh")
        os.chdir(cp)

def plot_k_grid():
# === Your data here ===
    cp = os.getcwd()
    pairs = []  # (k, E) pairs, sorted by k before plotting
    for k_grid_dir in os.listdir(cp):
        if os.path.isdir(k_grid_dir):
            try:
                k = int(k_grid_dir)
                with open(f'{cp}/{k_grid_dir}/aims.out', 'r') as f:
                    for line in f:
                        if '| Total energy of the DFT / Hartree-Fock s.c.f. calculation' in line:
                            pairs.append((k, float(line.split()[-2])))
            except (ValueError, FileNotFoundError, OSError):
                continue
    pairs.sort()
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]

    # how to plot the derivative of the energy with respect to the k-grid?
    #   1. calculate the derivative of the energy with respect to the k-grid
    #   2. plot the derivative of the energy with respect to the k-grid
    # === Plotting ===
    # System label from the directory layout (cwd is the kpts folder):
    # .../Si/kpts -> "Si";  .../Fe/LDA/BCC/kpts -> "Fe LDA BCC"
    parts = os.path.normpath(cp).split(os.sep)
    if len(parts) >= 4 and parts[-2].upper() in ("BCC", "FCC"):
        label = " ".join(parts[-4:-1])
    else:
        label = parts[-2] if len(parts) >= 2 else ""

    # Energies relative to the finest grid, in meV (1 meV = the convergence
    # criterion used throughout the tutorial).
    y = [(e - y[-1]) * 1000.0 for e in y]
    y_derivative = [abs(y[i+1] - y[i]) for i in range(len(y)-1)]
    x_derivative = x[:-1]

    plt.figure(figsize=(9, 5))
    plt.axhspan(-1, 1, color='green', alpha=0.12, label='±1 meV')
    plt.plot(x, y, marker='o', linestyle='-', linewidth=1.8, markersize=7)
    plt.xlabel('k-grid n (n×n×n)', fontsize=13)
    plt.ylabel('E − E(n=%d)  (meV)' % x[-1], fontsize=13)
    plt.title(f'k-point convergence — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('kgrid_convergence.png', dpi=200)
    plt.close()

    plt.figure(figsize=(9, 5))
    plt.plot(x_derivative, y_derivative, marker='s', linestyle='-',
             linewidth=1.8, markersize=7, color='tab:red')
    plt.axhline(y=1.0, color='green', linestyle='--', label='1 meV threshold')
    plt.yscale('log')
    plt.xlabel('k-grid n (n×n×n)', fontsize=13)
    plt.ylabel('|ΔE per step|  (meV)', fontsize=13)
    plt.title(f'k-point convergence rate — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('kgrid_derivative_convergence.png', dpi=200)
    plt.close()

def make_Fe_grid_search(lattice_type):
    cp = os.getcwd()
    # upper bound 4.55 so the 4.5 Å endpoint is included despite float rounding
    if lattice_type == "bcc":
        a_range = np.arange(2.0, 4.55, 0.25)
    elif lattice_type == "fcc":
        a_range = np.arange(3.0, 4.55, 0.25)
    else:
        raise ValueError(f"Invalid lattice type: {lattice_type}")
    # magnetic run? (spin collinear in control.in -> each atom needs an initial
    # spin guess, otherwise FHI-aims converges to the non-magnetic solution)
    magnetic = False
    if os.path.exists("control.in"):
        with open("control.in") as f:
            for line in f:
                keywords = line.split("#")[0].split()
                if len(keywords) >= 2 and keywords[0] == "spin" and keywords[1] == "collinear":
                    magnetic = True
    for a in a_range:
        if os.path.exists(f"{cp}/{a}"):
            continue
        os.makedirs(f"{cp}/{a}")
        if not os.path.exists(f"submit.sh"):
            raise FileNotFoundError(f"submit.sh not found in {cp}")
        if not os.path.exists(f"control.in"):
            raise FileNotFoundError(f"control.in not found in {cp}")
        os.system(f"cp submit.sh {cp}/{a}/submit.sh")
        os.system(f"cp control.in {cp}/{a}/control.in")
        # build the geometry.in
        # BCC Iron with lattice constant 3.0 Å
        if lattice_type == "bcc":
            iron_prim = bulk('Fe', crystalstructure='bcc', a=a)
        elif lattice_type == "fcc":
            iron_prim = bulk('Fe', crystalstructure='fcc', a=a)
        else:
            raise ValueError(f"Invalid lattice type: {lattice_type}")
        write(f"{cp}/{a}/geometry.in", iron_prim)
        # for magnetic runs, every atom needs an initial spin guess; ASE may
        # already write one (bulk Fe carries a default moment), so only add
        # initial_moment after atoms that don't have one yet
        if magnetic:
            with open(f"{cp}/{a}/geometry.in") as f:
                geo_lines = f.readlines()
            with open(f"{cp}/{a}/geometry.in", "w") as f:
                for i, line in enumerate(geo_lines):
                    f.write(line)
                    next_line = geo_lines[i + 1] if i + 1 < len(geo_lines) else ""
                    if line.lstrip().startswith("atom") and "initial_moment" not in next_line:
                        f.write("initial_moment 2\n")
        os.chdir(f"{cp}/{a}")
        os.system(f"sbatch submit.sh")
        os.chdir(cp)
    print("Have successfully prepared the Fe_grid_search")
    return 
def plot_Fe_grid_search():
    cp = os.getcwd()
    if os.path.exists(f"{cp}/2.0"):
        x = np.arange(2.0, 4.55, 0.25)
        print("BCC lattice type, if you want to plot for the FCC lattice type, please delete the folder under 3.0")
    else:
        x = np.arange(3.0, 4.55, 0.25)
        print("FCC lattice type")
    xs, y = [], []
    for a in x:
        e = None
        try:
            with open(f"{cp}/{a}/aims.out", "r") as f:
                for line in f:
                    if "| Total energy of the DFT / Hartree-Fock s.c.f. calculation" in line:
                        e = float(line.split()[-2])
        except FileNotFoundError:
            pass
        if e is None:
            print(f"Warning: no converged energy in {a}/aims.out - skipping this point "
                  f"(SCF may not have converged; try a larger smearing for that lattice constant)")
        else:
            xs.append(a)
            y.append(e)
    x = xs
    y = [i - min(y) for i in y]

    # Context label from the directory layout (cwd is lattice_grid):
    # .../Fe/LDA/BCC/mag/lattice_grid -> "Fe BCC mag (LDA)"
    parts = os.path.normpath(cp).split(os.sep)
    if len(parts) >= 5:
        label = f"{parts[-5]} {parts[-3]} {parts[-2]} ({parts[-4]})"
    else:
        label = "Fe"

    min_idx = int(np.argmin(y))
    plt.figure(figsize=(9, 5))
    plt.plot(x, y, marker='o', linestyle='-', linewidth=1.8, markersize=7)
    plt.plot(x[min_idx], y[min_idx], 'r*', markersize=18,
             label=f'minimum: a = {x[min_idx]:g} Å')
    plt.xlabel('Lattice constant a (Å)', fontsize=13)
    plt.ylabel('E − E_min  (eV)', fontsize=13)
    plt.title(f'Energy vs lattice constant — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('Fe_grid_search.png', dpi=200)
    plt.close()
    print(f"Have successfully plotted the Fe_grid_search ({label}, a_min = {x[min_idx]:g} Å)")

def get_lattice_constant(file_name):
    atoms = read(file_name, format="aims")
    # Use ASE's standardize_cell to get conventional cell
    cell_bravais = atoms.cell.get_bravais_lattice().conventional()
    conventional_lengths = cell_bravais.tocell().lengths()
    print("Conventional cell lattice constants: " + str(conventional_lengths))
    print("Primitive cell lattice constants: " + str(atoms.cell.lengths()))
    return 

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--make_k_grid", action="store_true", help="make the k-grid")
    parser.add_argument("--plot_k_grid", action="store_true", help="plot the k-grid")
    parser.add_argument("--k_grid_min", type=int, default=4, help="the k-grid min")
    parser.add_argument("--k_grid_max", type=int, default=12, help="the k-grid max")
    parser.add_argument("--Fe_grid_search", action="store_true", help="make the Fe_grid_search")
    parser.add_argument("--plot_Fe_grid_search", action="store_true", help="plot the Fe_grid_search")
    parser.add_argument("--lattice_type", type=str, default="bcc", choices=["bcc", "fcc"], help="Define the lattice type of Iron")
    parser.add_argument("--get_lattice_constant", action="store_true", help="get the lattice constant")
    parser.add_argument("--lattice_file_name", type=str, default="geometry.in.next_step", help="the file name of the structure file to get the lattice constant")
    args = parser.parse_args()
    if args.make_k_grid:
        print(args.k_grid_min, args.k_grid_max)
        make_k_grid(args.k_grid_min, args.k_grid_max)
    if args.plot_k_grid:
        plot_k_grid()
    if args.Fe_grid_search:
        make_Fe_grid_search(args.lattice_type)
    if args.plot_Fe_grid_search:
        plot_Fe_grid_search()
    if args.get_lattice_constant:
        get_lattice_constant(args.lattice_file_name)



