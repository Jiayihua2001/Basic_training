#!/bin/bash
#
# setup_utils.sh - Set up the tutorial utility scripts
#
# This script copies the 5 essential utility scripts into ONE folder,
# ~/aims_utils/, so you can run them from any working directory as
# ~/aims_utils/<script_name> without cluttering your home directory.
#
# All tools live under utils/: the cluster-independent helpers directly in
# utils/, and the cluster-specific submit.sh + write_control.py in
# utils/<cluster>/.
#
# Usage:
#   bash setup_utils.sh trace     # If you are on TRACE
#   bash setup_utils.sh mse-hpc   # If you are on MSE-HPC
#
# Files installed:
#   ~/aims_utils/write_control.py  - Generates control.in files for FHI-aims calculations.
#                         Reads species defaults and creates properly formatted
#                         control.in with the correct basis set settings.
#                         Usage: python ~/aims_utils/write_control.py --elements Si
#                                python ~/aims_utils/write_control.py --input_geometry --species_default light
#
#   ~/aims_utils/submit.sh         - SLURM batch script for submitting FHI-aims jobs on HPC.
#                         Pre-configured with the correct paths to the FHI-aims binary
#                         and appropriate resource settings for your cluster.
#                         Usage: sbatch ~/aims_utils/submit.sh
#                                cp ~/aims_utils/submit.sh .  (copy to working dir for automation scripts)
#
#   ~/aims_utils/automation.py     - Automation helper for Tutorial 2 (Periodic Systems).
#                         Automates k-point convergence tests, lattice constant scans,
#                         and plotting for Si, Na, Fe, and Ge calculations.
#                         Usage: python ~/aims_utils/automation.py --make_k_grid
#                                python ~/aims_utils/automation.py --plot_k_grid
#                                python ~/aims_utils/automation.py --Fe_grid_search --lattice_type bcc
#
#   ~/aims_utils/surfaces.py       - Automation helper for Tutorial 3 (2D Materials & Surfaces).
#                         Builds bilayer graphene, manages stacking configurations,
#                         runs vacuum/k-point convergence, distance scans, and
#                         TCNQ adsorption on graphene.
#                         Usage: python ~/aims_utils/surfaces.py --build_bilayer --stacking AA
#                                python ~/aims_utils/surfaces.py --make_k_grid_2d
#                                python ~/aims_utils/surfaces.py --place_tcnq_on_graphene --tcnq_site hollow
#
#   ~/aims_utils/aimsplot.py       - Plots band structure and DOS from an FHI-aims run.
#                         Reads band*.out and KS_DOS_total.dat files to generate
#                         combined band structure and DOS plots.
#                         Usage: python ~/aims_utils/aimsplot.py
#                                python ~/aims_utils/aimsplot.py --Emin -15 --Emax 10 --no-legend
#                                python ~/aims_utils/aimsplot.py --help
#

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check argument
if [ -z "$1" ]; then
    echo "Error: Please specify your HPC cluster."
    echo "Usage: bash setup_utils.sh trace"
    echo "       bash setup_utils.sh mse-hpc"
    exit 1
fi

HPC="$1"

if [ "$HPC" != "trace" ] && [ "$HPC" != "mse-hpc" ]; then
    echo "Error: Unknown HPC '$HPC'. Please use 'trace' or 'mse-hpc'."
    exit 1
fi

echo "Setting up utility scripts for $HPC (into ~/aims_utils/)..."
mkdir -p ~/aims_utils

# 1. write_control.py - Generates control.in for FHI-aims
echo "  Copying write_control.py ($HPC version)..."
cp "$SCRIPT_DIR/utils/$HPC/write_control.py" ~/aims_utils/write_control.py

# 2. submit.sh - SLURM batch script for FHI-aims
echo "  Copying submit.sh ($HPC version)..."
cp "$SCRIPT_DIR/utils/$HPC/submit.sh" ~/aims_utils/submit.sh

# 3. automation.py - Tutorial 2 automation (k-grid, lattice scans, plotting)
echo "  Copying automation.py..."
cp "$SCRIPT_DIR/utils/automation.py" ~/aims_utils/automation.py

# 4. surfaces.py - Tutorial 3 automation (bilayer, surfaces, adsorption)
echo "  Copying surfaces.py..."
cp "$SCRIPT_DIR/utils/surfaces.py" ~/aims_utils/surfaces.py

# 5. aimsplot.py - Band structure and DOS plotting
echo "  Copying aimsplot.py..."
cp "$SCRIPT_DIR/utils/aimsplot.py" ~/aims_utils/aimsplot.py

echo ""
echo "Done! The following files are now in ~/aims_utils/:"
echo "  ~/aims_utils/write_control.py  - Generate control.in files"
echo "  ~/aims_utils/submit.sh         - SLURM job submission script"
echo "  ~/aims_utils/automation.py     - Tutorial 2 automation (periodic systems)"
echo "  ~/aims_utils/surfaces.py       - Tutorial 3 automation (2D materials & surfaces)"
echo "  ~/aims_utils/aimsplot.py       - Band structure and DOS plotting"
echo ""
echo "You can now use them from any directory, e.g.:"
echo "  python ~/aims_utils/write_control.py --elements Si"
echo "  sbatch ~/aims_utils/submit.sh"
echo "  python ~/aims_utils/automation.py --make_k_grid"
echo "  python ~/aims_utils/surfaces.py --build_bilayer --stacking AA"
echo "  python ~/aims_utils/aimsplot.py"

# Verify the Python environment the helper scripts need (ASE).
echo ""
if python3 -c "import ase" >/dev/null 2>&1; then
    echo "Python check: OK ($(python3 -c 'import ase; print("ase", ase.__version__)'))"
else
    echo "NOTE: no Python with ASE is active, and the helper scripts need it."
    if [ "$HPC" = "mse-hpc" ]; then
        echo "  On MSE-HPC, use the shared conda to create YOUR OWN environment (one time):"
        echo "    source /mnt/beegfs/27-735/programs/miniforge3/etc/profile.d/conda.sh"
        echo "    conda create -n ase_env python=3.10"
        echo "    conda activate ase_env"
        echo "    pip install ase matplotlib numpy scipy spglib"
        echo "  In later sessions just source the first line and 'conda activate ase_env'"
        echo "  (see the MSE-HPC onboarding and Virtual Environments pages of the docs)."
    else
        echo "  On TRACE, activate your conda environment with ASE"
        echo "  (see the Virtual Environments page of the onboarding docs)."
    fi
fi
