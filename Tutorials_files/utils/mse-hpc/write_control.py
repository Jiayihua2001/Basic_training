from ase.io import read
from pathlib import Path
import numpy as np
import argparse

# === Constants ===
# MSE-HPC: species defaults come from the group's shared FHI-aims install.
BASE_SPECIES_PATH = Path('/mnt/beegfs/27-735/programs/fhi-aims.250822/species_defaults/defaults_2020')
SYMBOL_TO_ELE = {'H': "01", 'C': "06", 'N': "07", 'O': "08", 'S': "16", 'Cl': "17", 'Br': "35", 'I': "53", 'Na': "11", 'Si': "14", 'Fe': "26", 'Ge': "32"}

SETTINGS = {
    'xc': 'pw-lda', 'spin': 'none', 'relativistic': 'none', 'charge': 0, 'hessian_to_restart_geometry': '.false.','KS_method':'parallel'}

# === Utility Functions ===
def get_species_path(base_path: Path, species_default: str) -> Path:
    species_default_list = ['light', 'tight', 'intermediate']
    print(f"species_default: {species_default}")
    if species_default not in species_default_list:
        raise ValueError(f"Invalid species_default: choose from {species_default_list}")
    return base_path / species_default

def unique_ordered(array):
    _, idx = np.unique(array, return_index=True)
    return array[np.sort(idx)]

def write_control_file(struct, species_path: Path, settings: dict):
    symbols = unique_ordered(np.array(struct.get_chemical_symbols()))
    atomic_numbers = unique_ordered(struct.get_atomic_numbers())
    element_ids = [f"{num:02d}" for num in atomic_numbers]

    with open('control.in', 'w') as f:
        for setting, value in settings.items():
            f.write(f'{setting}    {value}\n')

    species_files = [species_path / f"{ele}_{sym}_default" for ele, sym in zip(element_ids, symbols)]
    for file_path in species_files:
        with open(file_path, 'r') as species, open('control.in', 'a') as control:
            control.writelines(species.readlines())

def write_by_element(species_path: Path, elements: list, settings: dict):
    with open('control.in', 'w') as f:
        for setting, value in settings.items():
            f.write(f'{setting}    {value}\n')

    for symbol in elements:
        path = species_path / f"{SYMBOL_TO_ELE[symbol]}_{symbol}_default"
        with open(path, 'r') as species, open('control.in', 'a') as control:
            control.writelines(species.readlines())

# === Main Workflow ===
def main(args):
    print(f"species_default: {repr(args.species_default)}")
    if args.species_default not in ['light', 'tight', 'intermediate']:
        raise ValueError(f"Invalid species_default: choose from {['light', 'heavy', 'intermediate']}")

    species_path = get_species_path(BASE_SPECIES_PATH, args.species_default)
    if args.input_geometry:
        struct = read('geometry.in')
        write_control_file(struct, species_path, SETTINGS.copy())
    else:
        write_by_element(species_path, args.elements, SETTINGS.copy())

# === Argument Parser ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FHI-aims control.in file.")
    parser.add_argument('--species_default', choices=['light', 'tight', 'intermediate'], default='light', help='Orbital basis type, light is default')
    parser.add_argument('--input_geometry', action='store_true', help='Input geometry.in file to detect elements and write control.in')
    parser.add_argument('--elements', nargs='+', default=['C', 'H', 'O', 'N'], help='Element list for species_define mode')

    args = parser.parse_args()
    main(args)
