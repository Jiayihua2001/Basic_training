"""
surfaces.py - Comprehensive utility library for Tutorial 3
DFT calculations for van der Waals-layered systems and surfaces

This module provides comprehensive functionality for:
- Bilayer graphene structure building and stacking configurations
- k-point and vacuum convergence testing for 2D systems
- Binding energy calculations and analysis
- Metal and graphene slab construction
- Molecule-on-surface adsorption (TCNQ on graphene)
- Automated plotting and convergence analysis
- Height-dependent adsorption energy scanning

Usage:
    python surfaces.py --help

Examples:
    # Build bilayer graphene
    python surfaces.py --build_bilayer --stacking AB --interlayer_distance 3.30
    
    # k-point convergence
    python surfaces.py --make_k_grid_2d --k_grid_min 4 --k_grid_max 16
    python surfaces.py --plot_k_grid_2d
    
    # TCNQ adsorption
    python surfaces.py --place_tcnq_on_graphene --tcnq_site hollow --tcnq_orientation x

Author: Tutorial 3 Materials
"""

import numpy as np
import os
import matplotlib.pyplot as plt
import argparse
from pathlib import Path

# Import ASE modules
from ase.build import graphene, fcc111, molecule
from ase.io import read, write
from ase import Atoms

# ============================================================================
# PART 1: BILAYER GRAPHENE STRUCTURE BUILDING
# ============================================================================

def build_bilayer_graphene(interlayer_distance=3.30, vacuum=10.0, 
                          stacking="AA", output_file="geometry.in"):
    """
    Build bilayer graphene structure with specified stacking.
    
    Parameters
    ----------
    interlayer_distance : float
        Distance between layers in Angstrom (default: 3.30)
    vacuum : float
        Vacuum spacing in z-direction in Angstrom (default: 10.0)
    stacking : str
        Stacking type: "AA" or "AB" (default: "AA")
    output_file : str
        Output filename (default: "geometry.in")
        
    Returns
    -------
    bilayer : ase.Atoms
        Bilayer graphene structure
    """
    # Build single layer graphene (primitive cell: 2 atoms)
    layer1 = graphene(vacuum=0)
    cell = layer1.get_cell()
    print(f"Unit cell vectors:\n{cell}")
    positions_layer1 = layer1.get_positions()
    
    # Create second layer
    positions_layer2 = positions_layer1.copy()
    positions_layer2[:, 2] += interlayer_distance
    
    # Apply stacking shift
    if stacking.upper() == "AB":
        # AB (Bernal) stacking: shift by 2/3 of lattice vector
        shift = (cell[0]/2 + cell[1]) * 2/3.0
        positions_layer2[:, 0] += shift[0]
        positions_layer2[:, 1] += shift[1]
    elif stacking.upper() == "AA":
        pass  # No shift needed for AA stacking
    else:
        raise ValueError(f"Invalid stacking type: {stacking}. Choose 'AA' or 'AB'.")
    
    # Combine layers
    all_positions = np.vstack([positions_layer1, positions_layer2])
    bilayer = Atoms('C4', positions=all_positions, cell=cell, pbc=[True, True, True])
    bilayer.center(vacuum=vacuum/2, axis=2)
    
    # Write to file
    write(output_file, bilayer, format='aims')
    print(f"✓ Created {output_file}: {stacking} stacking, d={interlayer_distance:.2f} Å, vac={vacuum:.1f} Å")
    
    return bilayer


def create_distance_scan(stacking="AB", distance_range=None, vacuum=10.0, 
                        auto_submit=True):
    """
    Create multiple bilayer structures scanning interlayer distances.
    Useful for binding energy curve calculations.
    
    Parameters
    ----------
    stacking : str
        Stacking type ("AA" or "AB")
    distance_range : list or None
        List of interlayer distances to scan (default: 3.0 to 4.5 with a step 0.1 Å)
    vacuum : float
        Vacuum spacing in Angstrom
    auto_submit : bool
        Automatically submit jobs (default: True)
        
    Returns
    -------
    distance_range : list
        List of distances used
    """
    if distance_range is None:
        distance_range = np.arange(3.0, 4.55, 0.1)  # include the 4.5 endpoint
    
    print(f"\n{'='*70}")
    print(f"Generating {stacking.upper()} stacking distance scan...")
    print(f"{'='*70}")
    
    cp = os.getcwd()
    sub_path = os.path.abspath("submit.sh")
    control_path = os.path.abspath("control.in")
    
    # Check required files
    if auto_submit:
        if not os.path.exists(sub_path):
            print(f"Warning: submit.sh not found. Jobs will not be submitted.")
            auto_submit = False
        if not os.path.exists(control_path):
            print(f"Warning: control.in not found.")
    
    for d in distance_range:    
        os.makedirs(f"d_{d:.2f}", exist_ok=True)
        output_file = f"d_{d:.2f}/geometry.in"
        
        build_bilayer_graphene(
            interlayer_distance=d, 
            vacuum=vacuum, 
            stacking=stacking, 
            output_file=output_file
        )
        
        if auto_submit:
            os.chdir(f"d_{d:.2f}")
            os.system(f"cp {sub_path} .")
            os.system(f"cp {control_path} .")
            os.system(f"sbatch submit.sh")
            os.chdir(cp)
    
    print(f"\n✓ Generated {len(distance_range)} structures")
    return distance_range


def create_vacuum_series(vacuum_list=None, interlayer_distance=3.30, 
                        stacking="AB", auto_submit=True,EX_step=1):
    """
    Generate bilayer structures with different vacuum spacings.
    Useful for vacuum convergence tests.
    
    Parameters
    ----------
    vacuum_list : list or None
        List of vacuum spacings (default: [10, 15, 20, 25, 30])
    interlayer_distance : float
        Fixed interlayer distance
    stacking : str
        Stacking type
    auto_submit : bool
        Automatically submit jobs
    """
    if vacuum_list is None:
        # start at 15 A: with use_dipole_correction, 10 A leaves too little
        # vacuum for the dipole-correction plane and FHI-aims refuses to run
        vacuum_list = [15, 20, 25, 30, 35, 40, 45, 50]
    
    print(f"\n{'='*70}")
    print(f"Generating vacuum convergence series...")
    print(f"{'='*70}")
    
    cp = os.getcwd()
    sub_path = os.path.abspath("submit.sh")
    control_path = os.path.abspath("control.in")
    
    if auto_submit:
        if not os.path.exists(sub_path) or not os.path.exists(control_path):
            print(f"Warning: Required files not found. Jobs will not be submitted.")
            auto_submit = False
    
    for vac in vacuum_list:
        os.makedirs(f"vac_{vac}", exist_ok=True)
        output_file = f"vac_{vac}/geometry.in"
        if EX_step == 1:
            build_bilayer_graphene(
                interlayer_distance=interlayer_distance,
                vacuum=vac, 
                stacking=stacking, 
                output_file=output_file
            )
        elif EX_step == 2:
            place_tcnq_on_graphene(
                surface_geometry='geometry_graphene.in',
                site='hollow',
                orientation='x',
                height=3.5,
                output_file=output_file,
                vacuum=vac
            )
            
        else:
            raise ValueError(f"Invalid EX_step: {EX_step}. Choose 1 or 2.")
            
        if auto_submit:
            os.chdir(f"vac_{vac}")
            os.system(f"cp {sub_path} .")
            os.system(f"cp {control_path} .")
            os.system("sbatch submit.sh")
            os.chdir(cp)
    
    print(f"\n✓ Generated {len(vacuum_list)} vacuum structures")

# ============================================================================
# PART 2: METAL SLAB CONSTRUCTION
# ============================================================================

def build_metal_slab(element='Au', layers=5, vacuum=15.0, 
                    size=(4, 4), a=None, output_file=None):
    """
    Build FCC metal (111) slab structure.
    
    Parameters
    ----------
    element : str
        Chemical symbol (e.g., 'Au', 'Pt', 'Cu', 'Ag')
    layers : int
        Number of atomic layers in z-direction
    vacuum : float
        Vacuum spacing in Angstrom (on each side)
    size : tuple
        Supercell size (nx, ny) in x and y directions
    a : float or None
        Lattice constant (if None, use default values)
    output_file : str or None
        Output filename (if None, auto-generate)
        
    Returns
    -------
    slab : ase.Atoms
        Metal slab structure
    """
    # Default lattice constants (Angstrom)
    if a is None:
        lattice_dict = {
            'Au': 4.08,  # Gold
            'Pt': 3.92,  # Platinum
            'Cu': 3.61,  # Copper
            'Ag': 4.09   # Silver
        }
        a = lattice_dict.get(element, 4.0)
        print(f"Using lattice constant: {a:.3f} Å for {element}")
    
    # Build FCC(111) slab
    # Note: size=(nx, ny, layers) where nx, ny are supercell repetitions
    slab = fcc111(element, size=(*size, layers), a=a, vacuum=vacuum, orthogonal=True)
    
    # Center the slab in the cell with equal vacuum on both sides
    slab.center(vacuum=vacuum/2, axis=2)
    
    # Generate output filename if not provided
    if output_file is None:
        output_file = f"geometry_{element}111_{layers}layers.in"
    
    # Write to FHI-aims format
    write(output_file, slab, format='aims')
    print(f"✓ Created {output_file}: {element}(111), {layers} layers, {len(slab)} atoms")
    print(f"  Cell dimensions: {slab.cell[0][0]:.2f} × {slab.cell[1][1]:.2f} × {slab.cell[2][2]:.2f} Å")
    
    return slab


def build_graphene_slab(layers=2, vacuum=15.0, size=(4, 4), output_file=None):
    """
    Build graphene slab for adsorption studies.
    Based on TCNQ_C/graphene.in reference file.
    
    Parameters
    ----------
    layers : int
        Number of graphene layers (default: 2)
    vacuum : float
        Vacuum spacing in z-direction (Angstrom)
    size : tuple
        Supercell size (nx, ny) for graphene
    output_file : str or None
        Output filename
    """
    from ase.build import graphene
    
    # Build single layer graphene
    layer1 = graphene(vacuum=0)
    
    if layers == 1:
        # Single layer
        slab = layer1.repeat((*size, 1))
    else:
        # Multiple layers with interlayer spacing
        interlayer_distance = 3.35  # Å
        all_layers = [layer1]
        
        for i in range(1, layers):
            new_layer = layer1.copy()
            new_layer.translate([0, 0, i * interlayer_distance])
            all_layers.append(new_layer)
        
        # Combine layers
        slab = all_layers[0]
        for layer in all_layers[1:]:
            slab.extend(layer)
        
        # Create supercell
        slab = slab.repeat((*size, 1))
    
    # Add vacuum
    slab.center(vacuum=vacuum/2, axis=2)
    
    if output_file is None:
        if layers == 1:
            output_file = f"geometry_graphene.in"
        else:
            output_file = f"geometry_graphene_{layers}layers.in"
    
    write(output_file, slab, format='aims')
    print(f"✓ Created {output_file}: Graphene, {layers} layers, {len(slab)} atoms")
    
    return slab

def create_slab_thickness_series(element='Au', layer_list=None, 
                                 vacuum=15.0, size=(4, 4)):
    """
    Create multiple slabs with different thicknesses for convergence testing.
    
    Parameters
    ----------
    element : str
        Metal element
    layer_list : list or None
        List of layer numbers (default: [3, 5, 7, 9])
    vacuum : float
        Vacuum spacing
    size : tuple
        Supercell size
    """
    if layer_list is None:
        layer_list = [3, 5, 7, 9]
    
    print(f"\n{'='*70}")
    print(f"Generating {element}(111) slab thickness series...")
    print(f"{'='*70}")
    
    for n_layers in layer_list:
        build_metal_slab(
            element=element, 
            layers=n_layers, 
            vacuum=vacuum, 
            size=size
        )
    
    print(f"\n✓ Generated {len(layer_list)} slab structures")

def create_graphene_thickness_series(layer_list=None, vacuum=15.0, size=(4, 4)):
    """
    Create multiple graphene slabs with different thicknesses for convergence testing.
    
    Parameters
    ----------
    layer_list : list or None
        List of layer numbers (default: [1, 2, 3])
    vacuum : float
        Vacuum spacing
    size : tuple
        Supercell size
    """
    if layer_list is None:
        layer_list = [1, 2, 3]
    
    print(f"\n{'='*70}")
    print(f"Generating graphene slab thickness series...")
    print(f"{'='*70}")
    
    for n_layers in layer_list:
        build_graphene_slab(
            layers=n_layers, 
            vacuum=vacuum, 
            size=size
        )
    
    print(f"\n✓ Generated {len(layer_list)} graphene slab structures")

# ============================================================================
# PART 3: MOLECULE BUILDING
# ============================================================================

def build_molecule(mol_name='benzene', output_file=None, rotate_flat=True):
    """
    Build common molecules for adsorption studies.
    
    Parameters
    ----------
    mol_name : str
        Molecule name: 'benzene', 'CO', 'H2O', 'CH4', 'NH3', 'tcnq'
    output_file : str or None
        Output filename (if None, auto-generate)
    rotate_flat : bool
        Rotate benzene to be flat (default: True)
        
    Returns
    -------
    mol : ase.Atoms
        Molecule structure
    """
    mol_dict = {
        'benzene': 'C6H6',
        'co': 'CO',
        'h2o': 'H2O',
        'ch4': 'CH4',
        'nh3': 'NH3',
        'tcnq': 'C12H4N4'  # Tetracyanoquinodimethane
    }
    
    mol_formula = mol_dict.get(mol_name.lower(), mol_name)
    
    # Special handling for TCNQ - build manually using reference structure
    if mol_name.lower() == 'tcnq':
        mol = build_tcnq_molecule()
    else:
        try:
            mol = molecule(mol_formula)
        except Exception as e:
            raise ValueError(f"Could not build molecule '{mol_name}': {e}\n"
                            f"Available: {list(mol_dict.keys())}")
    
    # Rotate benzene to be flat (ring parallel to xy-plane)
    if mol_name.lower() == 'benzene' and rotate_flat:
        mol.rotate(90, 'x')
    
    # Rotate TCNQ to be planar (flat on surface)
    if mol_name.lower() == 'tcnq':
        mol.rotate(90, 'x')  # Make TCNQ planar for surface adsorption
    
    if output_file is None:
        output_file = f"{mol_name.lower()}.in"
    
    write(output_file, mol, format='aims')
    print(f"✓ Created {output_file}: {mol_formula}, {len(mol)} atoms")
    
    return mol

def build_tcnq_molecule():
    """
    Build TCNQ (tetracyanoquinodimethane) molecule using reference structure.
    Based on TCNQ_C/TCNQ.in reference file.
    TCNQ formula: C12H4N4
    Structure: planar aromatic molecule with cyano groups
    """
    from ase import Atoms
    
    # TCNQ structure from reference file (TCNQ_C/TCNQ.in)
    # Coordinates in Angstrom, centered and oriented for adsorption
    positions = [
        # Nitrogen atoms (4 N atoms from cyano groups)
        [-4.0296, -2.2459, 0.0013],   # N1
        [-4.0301, 2.2457, -0.0013],    # N2
        [4.0296, -2.2458, -0.0004],    # N3
        [4.0299, 2.2458, 0.0022],       # N4
        
        # Central ring carbon atoms (8 C atoms)
        [-1.4081, 0.0000, 0.0001],     # C1
        [1.4081, -0.0001, -0.0008],    # C2
        [0.6725, -1.2668, -0.0009],    # C3
        [-0.6725, -1.2668, -0.0002],   # C4
        [0.6725, 1.2668, -0.0007],     # C5
        [-0.6724, 1.2668, -0.0003],    # C6
        [-2.7512, 0.0000, 0.0007],     # C7
        [2.7512, 0.0000, -0.0006],     # C8
        
        # Cyano group carbon atoms (4 C atoms)
        [-3.4535, -1.2384, 0.0012],    # C9
        [-3.4536, 1.2384, -0.0004],    # C10
        [3.4536, -1.2384, -0.0006],    # C11
        [3.4535, 1.2385, 0.0010],     # C12
        
        # Hydrogen atoms (4 H atoms)
        [1.1784, -2.2254, -0.0013],    # H1
        [1.1785, 2.2253, -0.0011],     # H2
        [-1.1785, -2.2254, -0.0003],   # H3
        [-1.1785, 2.2254, -0.0003],    # H4
    ]
    
    symbols = ['N'] * 4 + ['C'] * 12 + ['H'] * 4
    
    tcnq = Atoms(symbols=symbols, positions=positions)
    
    # Center the molecule
    tcnq.center()
    
    return tcnq

# ============================================================================
# PART 4: MOLECULE-ON-SURFACE ADSORPTION
# ============================================================================

def place_tcnq_on_graphene(
    surface_geometry='geometry_graphene.in',
    site='hollow',
    orientation='x',
    height=3.5,
    output_file=None,
    fix_bottom_layers=1,
    visualize=False,
    return_site_info=False,
    center_on_cell=True,
    vacuum=30.0
):
    """
    Place TCNQ molecule on graphene surface at specific adsorption sites.
    Based on adsorption sites diagram showing 6 configurations:
    bridge-x, bridge-y, hollow-x, hollow-y, top-x, top-y
    
    Parameters
    ----------
    surface_geometry : str
        Path to graphene slab geometry file
    site : str
        Adsorption site: 'top', 'bridge', 'hollow'
    orientation : str
        Molecule orientation: 'x' or 'y'
    height : float
        Height above surface in Angstrom (default: 2.5)
    output_file : str or None
        Output filename
    fix_bottom_layers : int or None
        Number of bottom layers to fix
    visualize : bool
        Open ASE GUI for visualization
    return_site_info : bool
        Return site information
        
    Returns
    -------
    combined : ase.Atoms
        Combined graphene + TCNQ system
    """
    from ase.geometry import get_layers
    from ase.constraints import FixAtoms
    
    # Read graphene slab
    slab = read(surface_geometry)
    
    # Build TCNQ molecule
    tcnq = build_tcnq_molecule()
    
    # Apply orientation (x or y)
    # ORIENTATION EXPLANATION:
    # - x orientation: TCNQ horizontal, hydrogen atoms along edges fall over graphene atoms/bonds
    # - y orientation: TCNQ vertical, hydrogen atoms along edges fall within hexagon areas
    # The difference affects how peripheral atoms interact with the graphene lattice
    if orientation.lower() == 'y':
        tcnq.rotate(90, 'z')  # Rotate 90 degrees around z-axis
    
    # Identify surface layer
    try:
        layers, layer_indices = get_layers(slab, (0, 0, 1))
        surface_layer = max(layers)
        surface_atom_indices = [i for i, layer in enumerate(layers) if layer == surface_layer]
        surface_xyz = slab.positions[surface_atom_indices]
        z_surf = np.mean([pos[2] for pos in surface_xyz])
    except:
        # Fallback method
        z_coords = np.array([pos[2] for pos in slab.positions])
        z_surf = np.max(z_coords)
        tol = 0.15
        surface_atom_indices = np.where(np.abs(z_coords - z_surf) < tol)[0]
        surface_xyz = slab.positions[surface_atom_indices]
    
    # Determine adsorption site position based on site and orientation
    if site.lower() == 'top':
        # Top site: above carbon atoms
        if orientation.lower() == 'x':
            # Vertical orientation: N atoms above C atoms
            pos_site = surface_xyz[0]  # Use first surface atom
        else:  # y orientation
            pos_site = surface_xyz[0]  # Use first surface atom
            
    elif site.lower() == 'bridge':
        # Bridge site: above C-C bonds
        if len(surface_xyz) < 2:
            raise ValueError('Bridge site requires at least 2 surface atoms')
        # Find two closest surface atoms
        distances = np.linalg.norm(surface_xyz[:, None] - surface_xyz[None, :], axis=2)
        np.fill_diagonal(distances, np.inf)
        min_idx = np.unravel_index(np.argmin(distances), distances.shape)
        pos_site = (surface_xyz[min_idx[0]] + surface_xyz[min_idx[1]]) / 2
        
    elif site.lower() == 'hollow':
        # Detect aromatic ring C-C bond length from the graphene slab
        # Only consider surface carbon atoms (assuming carbon atomic number = 6)
        surface_elements = [slab[i].number for i in surface_atom_indices]
        surface_carbons = [i for i, el in zip(surface_atom_indices, surface_elements) if el == 6]
        c_c_bond = None
        if len(surface_carbons) > 1:
            surface_carbon_positions = slab.positions[surface_carbons]
            # Compute all pairwise distances
            try:
                from scipy.spatial.distance import pdist
                distances = pdist(surface_carbon_positions)
            except ImportError:
                # Fallback: compute pairwise distances manually
                distances = []
                for i in range(len(surface_carbon_positions)):
                    for j in range(i+1, len(surface_carbon_positions)):
                        dist = np.linalg.norm(surface_carbon_positions[i] - surface_carbon_positions[j])
                        distances.append(dist)
                distances = np.array(distances)
            # Typical C–C bond in aromatic ring ~1.42Å, take minimum for accuracy
            c_c_bond = np.min(distances)
        else:
            # Fallback to default if not enough C atoms detected
            c_c_bond = 1.42 # Å
        if orientation.lower() == 'x':
            tcnq.rotate(90, 'z')
            pos_site = surface_xyz[0] + np.array([0, c_c_bond, 0])
        else:  # y orientation
            
            pos_site = surface_xyz[0] + np.array([0,c_c_bond, 0])
            tcnq.rotate(90, 'z')
    else:
        raise ValueError("site must be one of: 'top', 'bridge', 'hollow'")

    # Translate TCNQ so its center of mass is at pos_site
    tcnq.translate(pos_site - tcnq.get_center_of_mass())
    tcnq_com = tcnq.get_center_of_mass()
    # Get supercell dimensions
    cell = slab.get_cell()
    

    # The cell is already in Cartesian coordinates; to find the geometric center,
    # take half the sum of the three cell vectors.
    pos_site_final = np.zeros(3)
    if center_on_cell:
        # List all combinations of periodic shifts by graphene unit cell (2.46 Å) in the xy-plane
        # within the bounds of the supercell and find the one closest to center
        graphene_uc = 2.46  # Graphene unit cell length in Angstroms

        # Get supercell bounds along a and b real-space directions
        # Assume cell[0] and cell[1] are the lattice vectors in x and y
        # Determine required number of periodic shifts from cell dimensions
        n_shift_a = int(np.ceil(np.linalg.norm(cell[0]) / graphene_uc))
        n_shift_b = int(np.ceil(np.linalg.norm(cell[1]) / graphene_uc))

        # Compute nominal supercell in-plane center
        cell_center = 0.5 * (cell[0][:2] + cell[1][:2])
        supercell_center = np.array([cell_center[0], cell_center[1], z_surf])
        # List all periodic translations of the TCNQ center using graphene_uc
        shifts = []
        for i in range(n_shift_a):
            for j in range(n_shift_b):
                shift_vec = i * graphene_uc * cell[0] / np.linalg.norm(cell[0]) \
                          + j * graphene_uc * cell[1] / np.linalg.norm(cell[1])
                shifts.append(shift_vec[:2])

        # Find the shift that puts TCNQ center closest to the supercell center
        best_distance = None
        best_shift = None
        best_pos_xy = None
        for shift in shifts:
            trial_com_xy = tcnq_com[:2] + np.array(shift)
            distance = np.linalg.norm(supercell_center[:2] - trial_com_xy)
            if (best_distance is None) or (distance < best_distance):
                best_distance = distance
                best_shift = shift
                best_pos_xy = trial_com_xy

        pos_site_final[0:2] = best_pos_xy
        pos_site_final[2] = pos_site[2] + height

        # Translate TCNQ by the selected periodic shift and height above surface
        tcnq.translate([best_shift[0], best_shift[1], height])
    else:
        pos_site_final[0:2] = tcnq_com[0:2]
        pos_site_final[2] = pos_site[2]+height
        tcnq.translate([0, 0, height])
    # Combine graphene and TCNQ
    combined = slab + tcnq
    combined.set_cell(slab.get_cell())
    combined.pbc = [True, True, True]
    
    # Add constraints if requested
    if fix_bottom_layers is not None and fix_bottom_layers > 0:
        try:
            layers, layer_indices = get_layers(combined, (0, 0, 1))
            unique_layers = sorted(set(layers))
            fixed_indices = []
            for i, layer in enumerate(layers):
                if layer in unique_layers[:fix_bottom_layers]:
                    fixed_indices.append(i)
            
            if fixed_indices:
                combined.set_constraint(FixAtoms(indices=fixed_indices))
                print(f"✓ Fixed {len(fixed_indices)} atoms in bottom {fix_bottom_layers} layers")
        except Exception as e:
            print(f"Warning: Could not apply layer constraints: {e}")
    
    # Combine slab and TCNQ together

    # Adjust the vacuum (add vacuum above and below)
    positions_z = combined.positions[:, 2]
    min_z, max_z = positions_z.min(), positions_z.max()
    buffer = vacuum/2  # Ångstroms of vacuum above and below
    new_cell = combined.get_cell().copy()
    current_height = max_z - min_z
    new_cell[2, 2] = current_height + 2 * buffer
    combined.set_cell(new_cell)
    # Center system in z
    combined.translate([0, 0, (buffer - min_z)])

    # Generate output filename
    if output_file is None:
        output_file = f'geometry_tcnq_{site}_{orientation}.in'
    # Write output
    write(output_file, combined, format='aims')
    print(f'✓ Placed TCNQ on {site}-{orientation} site: {output_file}')
    print(f'  Detected site: ({pos_site[0]:.3f}, {pos_site[1]:.3f}, {pos_site[2]:.3f}) Å')
    print(f'  🎯 Centered at supercell center: ({pos_site_final}) Å')
    print(f'  TCNQ height: {height:.2f} Å above surface')
    print(f'  Total atoms: {len(combined)}')
    
    # Optional visualization
    if visualize:
        try:
            from ase.visualize import view
            view(combined)
        except:
            print("Warning: Could not open visualization")
    
    # Return site information if requested
    if return_site_info:
        site_info = {
            'original_site_position': pos_site,
            'final_site_position': pos_site_final,
            'height_above_surface': height,
            'site_type': f"{site}-{orientation}",
        }
        return combined, site_info
    
    return combined

def create_tcnq_adsorption_series(
    surface_geometry='geometry_graphene.in',
    height=2.5,
    fix_bottom_layers=1,
    vacuum=30
):
    """
    Create all 6 TCNQ adsorption configurations based on adsorption sites diagram.
    Configurations: bridge-x, bridge-y, hollow-x, hollow-y, top-x, top-y
    
    Parameters
    ----------
    surface_geometry : str
        Path to graphene slab geometry file
    height : float
        Height above surface in Angstrom
    fix_bottom_layers : int
        Number of bottom layers to fix
        
    Returns
    -------
    results : dict
        Dictionary with configuration names as keys and structures as values
    """
    print(f"\n{'='*70}")
    print(f"Creating TCNQ adsorption series (6 configurations)")
    print(f"{'='*70}")
    
    sites = ['top', 'bridge', 'hollow']
    orientations = ['x', 'y']
    results = {}
    
    for site in sites:
        for orientation in orientations:
            config_name = f"{site}-{orientation}"
            try:
                combined = place_tcnq_on_graphene(
                    surface_geometry=surface_geometry,
                    site=site,
                    orientation=orientation,
                    height=height,
                    fix_bottom_layers=fix_bottom_layers,
                    output_file=f'geometry_tcnq_{site}_{orientation}.in',
                    vacuum=vacuum
                )
                results[config_name] = combined
                print(f"✓ Created {config_name} configuration")
            except Exception as e:
                print(f"✗ Failed to create {config_name}: {e}")
    
    print(f"\n✓ Created {len(results)}/6 TCNQ adsorption configurations")
    return results




def make_k_grid_2d(k_grid_min=4, k_grid_max=16, k_grid_step=2):
    """
    Create k-point convergence test directories for 2D systems.
    Uses n×n×1 k-grid format (appropriate for slabs/2D materials).
    
    Parameters
    ----------
    k_grid_min : int
        Minimum k-grid value
    k_grid_max : int
        Maximum k-grid value
    k_grid_step : int
        Step size for k-grid
    """
    cp = os.getcwd()
    
    # Check required files
    for req_file in ['submit.sh', 'control.in', 'geometry.in']:
        if not os.path.exists(req_file):
            raise FileNotFoundError(f"{req_file} not found in {cp}")
    
    print(f"\n{'='*70}")
    print(f"Setting up k-point convergence tests (2D format: n×n×1)")
    print(f"{'='*70}")
    
    for k in range(k_grid_min, k_grid_max + 1, k_grid_step):
        k_dir = f"k_{k}x{k}x1"
        
        if os.path.exists(k_dir):
            print(f"  {k_dir} already exists, skipping...")
            continue
        
        os.makedirs(k_dir)
        os.system(f"cp submit.sh control.in geometry.in {k_dir}/")
        
        # Modify control.in to add k_grid specification
        with open(f"{k_dir}/control.in", "r+") as f:
            lines = f.readlines()
            
            # Remove existing k_grid lines if present
            lines = [l for l in lines if not l.strip().startswith('k_grid')]
            
            # Find appropriate insertion point (after charge line or at end)
            insert_idx = len(lines)
            for i, line in enumerate(lines):
                if "charge" in line:
                    insert_idx = i + 1
                    break
            
            # Insert new k_grid specification
            lines.insert(insert_idx, f"k_grid  {k} {k} 1\n")
            
            f.seek(0)
            f.writelines(lines)
            f.truncate()
        
        # Submit job
        os.chdir(k_dir)
        os.system("sbatch submit.sh")
        os.chdir(cp)
        print(f"  ✓ Created and submitted: {k_dir}")
    
    print(f"\n✓ k-point convergence setup complete")

# ============================================================================
# PART 6: ENERGY EXTRACTION AND ANALYSIS
# ============================================================================

def extract_total_energy(aims_output="aims.out"):
    """
    Extract total energy from FHI-aims output file.
    
    Parameters
    ----------
    aims_output : str
        Path to aims.out file
        
    Returns
    -------
    energy : float or None
        Total energy in eV, or None if not found
    """
    try:
        with open(aims_output, 'r') as f:
            for line in f:
                if "| Total energy of the DFT / Hartree-Fock s.c.f. calculation" in line:
                    return float(line.split()[-2])
    except FileNotFoundError:
        print(f"Warning: {aims_output} not found")
        return None
    except Exception as e:
        print(f"Error reading {aims_output}: {e}")
        return None
    return None


def calculate_binding_energy(E_bilayer, E_monolayer):
    """
    Calculate binding energy for bilayer systems.
    
    E_binding = E_bilayer - 2 * E_monolayer
    
    Negative values indicate favorable binding.
    
    Parameters
    ----------
    E_bilayer : float
        Total energy of bilayer system (eV)
    E_monolayer : float
        Total energy of isolated monolayer (eV)
        
    Returns
    -------
    E_binding : float
        Binding energy in eV
    """
    return E_bilayer - 2 * E_monolayer


def calculate_adsorption_energy(E_total, E_slab, E_molecule):
    """
    Calculate adsorption energy for molecule-on-surface system.
    
    E_ads = E_total - E_slab - E_molecule
    
    Negative values indicate favorable adsorption.
    
    Parameters
    ----------
    E_total : float
        Total energy of combined system (eV)
    E_slab : float
        Total energy of bare slab (eV)
    E_molecule : float
        Total energy of isolated molecule (eV)
        
    Returns
    -------
    E_ads : float
        Adsorption energy in eV
    """
    return E_total - E_slab - E_molecule

# ============================================================================
# PART 7: PLOTTING AND VISUALIZATION
# ============================================================================

def plot_k_grid_2d():
    """
    Plot k-point convergence results for 2D systems.
    Collects data from k_*x*x1 directories and creates convergence plots.
    """
    cp = os.getcwd()
    x, y = [], []
    
    # Collect data from k_*x*x1 directories
    for dir_name in sorted(os.listdir(cp)):
        if dir_name.startswith('k_') and 'x' in dir_name:
            aims_out = os.path.join(cp, dir_name, 'aims.out')
            if os.path.exists(aims_out):
                try:
                    energy = extract_total_energy(aims_out)
                    if energy is not None:
                        y.append(energy)
                        # Extract k from directory name (k_12x12x1 -> 12)
                        k_val = int(dir_name.split('_')[1].split('x')[0])
                        x.append(k_val)
                except Exception as e:
                    print(f"Warning: Could not read {aims_out}: {e}")
    
    if len(x) == 0:
        print("Error: No data found for k-grid convergence")
        return
    
    # Sort by k-grid value
    sorted_pairs = sorted(zip(x, y))
    x, y = zip(*sorted_pairs)
    x, y = list(x), list(y)
    
    # System label from the directory layout (cwd is the k_grid folder):
    # .../bilayer_graphene/convergence/k_grid -> "bilayer graphene"
    parts = os.path.normpath(cp).split(os.sep)
    label = parts[-3].replace('_', ' ') if len(parts) >= 3 else '2D system'

    # Energies relative to the finest grid, in meV (the tutorial's convergence
    # criterion is |ΔE| < 1 meV).
    y_shifted = [(e - y[-1]) * 1000.0 for e in y]

    # Energy differences between consecutive points (meV)
    y_derivative = [abs(y_shifted[i+1] - y_shifted[i]) for i in range(len(y_shifted)-1)]
    x_derivative = x[:-1]

    # Plot 1: Energy convergence
    plt.figure(figsize=(9, 5))
    plt.axhspan(-1, 1, color='green', alpha=0.12, label='±1 meV')
    plt.plot(x, y_shifted, marker='o', linestyle='-', linewidth=1.8, markersize=7)
    plt.xlabel('k-grid n (n×n×1)', fontsize=13)
    plt.ylabel('E − E(n=%d)  (meV)' % x[-1], fontsize=13)
    plt.title(f'k-point convergence — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('kgrid_convergence_2d.png', dpi=200)
    print("✓ Saved: kgrid_convergence_2d.png")
    plt.close()

    # Plot 2: Energy derivative (convergence rate)
    plt.figure(figsize=(9, 5))
    plt.plot(x_derivative, y_derivative, marker='s', linestyle='-',
             linewidth=1.8, markersize=7, color='tab:red')
    plt.axhline(y=1.0, color='green', linestyle='--', label='1 meV threshold')
    plt.xlabel('k-grid n (n×n×1)', fontsize=13)
    plt.ylabel('|ΔE per step|  (meV)', fontsize=13)
    plt.title(f'k-point convergence rate — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('kgrid_derivative_2d.png', dpi=200)
    print("✓ Saved: kgrid_derivative_2d.png")
    plt.close()
    
    # Print summary table
    print(f"\n{'='*70}")
    print("k-Point Convergence Summary")
    print(f"{'='*70}")
    print(f"{'k-grid':<15} {'Energy (eV)':<20} {'|ΔE| (meV)':<15}")
    print(f"{'-'*70}")
    for i, (k_val, e) in enumerate(zip(x, y_shifted)):
        de = y_derivative[i]*1000 if i < len(y_derivative) else 0
        print(f"{k_val}×{k_val}×1{'':<7} {e:<20.6f} {de:<15.3f}")
    print(f"{'='*70}")


def plot_vacuum_convergence():
    """
    Plot vacuum convergence results.
    Collects data from vac_* directories.
    """
    cp = os.getcwd()
    x, y = [], []
    
    # Collect data from vac_* directories
    for dir_name in sorted(os.listdir(cp)):
        if dir_name.startswith('vac_'):
            aims_out = os.path.join(cp, dir_name, 'aims.out')
            if os.path.exists(aims_out):
                try:
                    energy = extract_total_energy(aims_out)
                    if energy is not None:
                        y.append(energy)
                        vac = int(dir_name.split('_')[1])
                        x.append(vac)
                except Exception as e:
                    print(f"Warning: Could not read {aims_out}: {e}")
    
    if len(x) == 0:
        print("Error: No data found for vacuum convergence")
        return
    
    # Sort by vacuum value
    sorted_pairs = sorted(zip(x, y))
    x, y = zip(*sorted_pairs)
    x, y = list(x), list(y)
    
    # System label from the directory layout (cwd is the vacuum folder)
    parts = os.path.normpath(cp).split(os.sep)
    label = parts[-3].replace('_', ' ') if len(parts) >= 3 else 'slab'

    # Plot energy CHANGE vs the largest vacuum, in meV. Plotting absolute
    # energies here lets matplotlib's offset notation blow µeV-level noise up
    # into a dramatic-looking curve — the classic way to over-read vacuum
    # convergence. On the meV scale relevant to the ±1 meV criterion, a
    # converged series is simply flat.
    y_rel = [(e - y[-1]) * 1000.0 for e in y]
    plt.figure(figsize=(9, 5))
    plt.axhspan(-1, 1, color='green', alpha=0.12, label='±1 meV')
    plt.plot(x, y_rel, marker='o', linestyle='-', linewidth=1.8, markersize=7)
    plt.xlabel('Vacuum (Å)', fontsize=13)
    plt.ylabel('E − E(vac=%g Å)  (meV)' % x[-1], fontsize=13)
    plt.title(f'Vacuum convergence — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('vacuum_convergence.png', dpi=200)
    print("✓ Saved: vacuum_convergence.png")
    plt.close()
    
    # Print summary
    print(f"\n{'='*70}")
    print("Vacuum Convergence Summary")
    print(f"{'='*70}")
    print(f"{'Vacuum (Å)':<15} {'Energy (eV)':<20} {'ΔE (meV)':<15}")
    print(f"{'-'*70}")
    for i, (vac, e) in enumerate(zip(x, y)):
        de = (y[i] - y[i-1])*1000 if i > 0 else 0
        print(f"{vac:<15} {e:<20.6f} {de:<15.3f}")
    print(f"{'='*70}")


def plot_binding_curve():
    """
    Plot binding energy curve vs interlayer distance.
    Collects data from d_* directories.
    Requires monolayer/aims.out for reference energy.
    
    Returns
    -------
    eq_distance : float
        Equilibrium interlayer distance
    eq_energy : float
        Binding energy at equilibrium
    """
    cp = os.getcwd()
    distances = []
    energies = []
    
    # Get monolayer energy for reference
    monolayer_path = os.path.join(cp, "monolayer", "aims.out")
    if not os.path.exists(monolayer_path):
        print("Error: monolayer/aims.out not found. Cannot calculate binding energy.")
        return None, None
    
    e_monolayer = extract_total_energy(monolayer_path)
    if e_monolayer is None:
        print("Error: Could not extract energy from monolayer/aims.out")
        return None, None
    
    # Collect bilayer energies
    for dir_name in os.listdir(cp):
        if dir_name.startswith("d_"):
            aims_out = os.path.join(cp, dir_name, "aims.out")
            if os.path.exists(aims_out):
                try:
                    distance = float(dir_name.split("_")[1])
                    e_bilayer = extract_total_energy(aims_out)
                    if e_bilayer is not None:
                        distances.append(distance)
                        e_binding = calculate_binding_energy(e_bilayer, e_monolayer)
                        energies.append(e_binding)
                except Exception as e:
                    print(f"Warning: Could not process {dir_name}: {e}")
    
    if len(distances) == 0:
        print("Error: No data found for binding curve")
        return None, None
    
    # Sort by distance
    sorted_pairs = sorted(zip(distances, energies))
    distances, energies = zip(*sorted_pairs)
    distances, energies = list(distances), list(energies)
    
    # Find equilibrium (minimum energy)
    min_idx = np.argmin(energies)
    eq_distance = distances[min_idx]
    eq_energy = energies[min_idx]
    
    # Context label from the directory layout (cwd is the functional folder):
    # .../stacking/AB/distance_scan/pbe_ts -> "AB, PBE+TS"
    func_names = {'pbe': 'PBE', 'pbe_ts': 'PBE+TS', 'pbe_mbd': 'PBE+MBD'}
    parts = os.path.normpath(cp).split(os.sep)
    func = func_names.get(parts[-1].lower(), parts[-1])
    stacking = parts[-3] if len(parts) >= 3 else ''
    label = f'{stacking}, {func}'.strip(', ')

    # Plot
    plt.figure(figsize=(9, 5))
    plt.plot(distances, energies, 'o-', linewidth=1.8, markersize=7,
             label='Binding energy')
    plt.plot(eq_distance, eq_energy, 'r*', markersize=18,
             label=f'Equilibrium: d={eq_distance:.2f} Å, E_b={eq_energy:.3f} eV')

    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    plt.xlabel('Interlayer Distance (Å)', fontsize=13)
    plt.ylabel('Binding Energy (eV)', fontsize=13)
    plt.title(f'Binding energy curve — {label}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig('binding_curve.png', dpi=200)
    print(f"✓ Saved: binding_curve.png")
    plt.close()
    
    # Print summary
    print(f"\n{'='*70}")
    print("Binding Energy Analysis")
    print(f"{'='*70}")
    print(f"Equilibrium distance: {eq_distance:.3f} Å")
    print(f"Binding energy: {eq_energy:.4f} eV")
    print(f"{'='*70}")
    
    return eq_distance, eq_energy


def compare_functionals(distances, energies_dict, stacking="AB", save_fig=True):
    """
    Compare binding curves for different DFT functionals.
    
    Parameters
    ----------
    distances : list
        List of interlayer distances
    energies_dict : dict
        Dictionary with functional names as keys and energy lists as values
    stacking : str
        Stacking type for plot title
    save_fig : bool
        Whether to save the figure
        
    Returns
    -------
    results : dict
        Dictionary with equilibrium properties for each functional
    """
    plt.figure(figsize=(12, 7))
    
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'brown', 'pink']
    markers = ['o', 's', '^', 'D', 'v', '<', '>']
    results = {}
    
    for idx, (functional, energies) in enumerate(energies_dict.items()):
        color = colors[idx % len(colors)]
        marker = markers[idx % len(markers)]
        
        plt.plot(distances, energies, marker=marker, linestyle='-', 
                linewidth=2, markersize=8, color=color, label=functional)
        
        # Find equilibrium
        min_idx = np.argmin(energies)
        eq_distance = distances[min_idx]
        eq_energy = energies[min_idx]
        results[functional] = {'d_eq': eq_distance, 'E_binding': eq_energy}
        
        # Mark equilibrium point
        plt.plot(eq_distance, eq_energy, '*', markersize=15, color=color, alpha=0.7)
    
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    plt.xlabel('Interlayer Distance (Å)', fontsize=14)
    plt.ylabel('Binding Energy (eV)', fontsize=14)
    plt.title(f'Functional Comparison - {stacking} Stacking', fontsize=16)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_fig:
        figname = f'binding_comparison_{stacking}.png'
        plt.savefig(figname, dpi=300)
        print(f"✓ Saved: {figname}")
    
    plt.show()
    
    # Print summary table
    print(f"\n{'='*70}")
    print(f"Equilibrium Properties - {stacking} Stacking")
    print(f"{'='*70}")
    print(f"{'Functional':<15} {'d_eq (Å)':<15} {'E_binding (eV)':<20}")
    print(f"{'-'*70}")
    for func, data in results.items():
        print(f"{func:<15} {data['d_eq']:<15.3f} {data['E_binding']:<20.4f}")
    print(f"{'='*70}")
    
    return results


def compare_adsorption_sites(site_energies, functional_name="PBE+vdW"):
    """
    Compare adsorption energies at different sites.
    
    Parameters
    ----------
    site_energies : dict
        Dictionary with site names as keys and adsorption energies as values
    functional_name : str
        Name of functional for plot title
        
    Returns
    -------
    best_site : str
        Most favorable adsorption site
    best_energy : float
        Adsorption energy at best site
    """
    sites = list(site_energies.keys())
    energies = list(site_energies.values())
    
    # Sort by energy (most favorable first)
    sorted_indices = np.argsort(energies)
    sites_sorted = [sites[i] for i in sorted_indices]
    energies_sorted = [energies[i] for i in sorted_indices]
    
    # Plot
    plt.figure(figsize=(10, 6))
    colors = ['green' if e < 0 else 'red' for e in energies_sorted]
    plt.bar(sites_sorted, energies_sorted, color=colors, alpha=0.7, edgecolor='black')
    
    for i, (site, energy) in enumerate(zip(sites_sorted, energies_sorted)):
        plt.text(i, energy, f'{energy:.3f}', 
                ha='center', va='bottom' if energy > 0 else 'top', fontsize=11)
    
    plt.axhline(y=0, color='k', linestyle='--', alpha=0.5)
    plt.ylabel('Adsorption Energy (eV)', fontsize=14)
    plt.xlabel('Adsorption Site', fontsize=14)
    plt.title(f'Adsorption Site Comparison - {functional_name}', fontsize=16)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    figname = f'adsorption_sites_{functional_name}.png'
    plt.savefig(figname, dpi=300)
    print(f"✓ Saved: {figname}")
    plt.show()
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Adsorption Site Summary - {functional_name}")
    print(f"{'='*70}")
    print(f"{'Site':<15} {'E_ads (eV)':<20}")
    print(f"{'-'*70}")
    for site, energy in zip(sites_sorted, energies_sorted):
        print(f"{site:<15} {energy:<20.4f}")
    print(f"{'='*70}")
    print(f"Most favorable: {sites_sorted[0]} ({energies_sorted[0]:.4f} eV)")
    print(f"{'='*70}")
    
    return sites_sorted[0], energies_sorted[0]


def create_height_scan_series(
    surface_geometry='geometry_graphene.in',
    site='hollow',
    orientation='x',
    height_range=None,
    height_step=0.1,
    auto_submit=True,
    vacuum=30.0
):
    """
    Create height-dependent adsorption energy scan for TCNQ on graphene.
    This function addresses the TODO mentioned in the tutorial.
    
    Parameters
    ----------
    surface_geometry : str
        Path to graphene slab geometry file
    site : str
        Adsorption site: 'top', 'bridge', 'hollow'
    orientation : str
        Molecule orientation: 'x' or 'y'
    height_range : list or None
        List of heights to scan (default: [2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4])
    height_step : float
        Step size for height scan (default: 0.2)
    auto_submit : bool
        Automatically submit jobs (default: True)
        
    Returns
    -------
    height_list : list
        List of heights used
    """
    if height_range is None:
        height_range = [ 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6]
    
    print(f"\n{'='*70}")
    print(f"Creating height scan for TCNQ adsorption ({site}-{orientation})")
    print(f"{'='*70}")
    
    cp = os.getcwd()
    sub_path = os.path.abspath("submit.sh")
    control_path = os.path.abspath("control.in")
    
    if auto_submit:
        if not os.path.exists(sub_path) or not os.path.exists(control_path):
            print(f"Warning: Required files not found. Jobs will not be submitted.")
            auto_submit = False
    
    for height in height_range:
        height_dir = f"h_{height:.1f}"
        os.makedirs(height_dir, exist_ok=True)
        
        # Create geometry with TCNQ at specific height
        try:
            combined = place_tcnq_on_graphene(
                surface_geometry=surface_geometry,
                site=site,
                orientation=orientation,
                height=height,
                output_file=f"{height_dir}/geometry.in",
                vacuum=vacuum
            )
            
            if auto_submit:
                os.system(f"cp {sub_path} {control_path} {height_dir}/")
                os.chdir(height_dir)
                os.system("sbatch submit.sh")
                os.chdir(cp)
            
            print(f"  ✓ Created: {height_dir} (height={height:.1f} Å)")
            
        except Exception as e:
            print(f"  ✗ Failed to create {height_dir}: {e}")
    
    print(f"\n✓ Generated {len(height_range)} height scan structures")
    return height_range


def plot_height_scan(
    site='hollow',
    orientation='x',
    functional_name='PBE+TS',
    save_fig=True,
    E_slab=None,
    E_molecule=None
):
    """
    Plot height-dependent adsorption energy curve.
    Collects data from h_* directories and creates adsorption curve.
    
    Parameters
    ----------
    site : str
        Adsorption site name
    orientation : str
        Molecule orientation
    functional_name : str
        Functional name for plot title
    save_fig : bool
        Whether to save the figure
        
    Returns
    -------
    optimal_height : float
        Height with minimum adsorption energy
    min_energy : float
        Minimum adsorption energy
    """
    cp = os.getcwd()
    heights = []
    energies = []
    
    # Collect data from h_* directories
    for dir_name in sorted(os.listdir(cp)):
        if dir_name.startswith('h_'):
            aims_out = os.path.join(cp, dir_name, 'aims.out')
            if os.path.exists(aims_out):
                try:
                    height = float(dir_name.split('_')[1])
                    energy = extract_total_energy(aims_out)
                    if energy is not None:
                        heights.append(height)
                        if E_slab is not None and E_molecule is not None:
                            E_adsorption = energy - E_slab - E_molecule
                            energies.append(E_adsorption)
                        else:
                            energies.append(energy)
                except Exception as e:
                    print(f"Warning: Could not read {aims_out}: {e}")
    
    if len(heights) == 0:
        print("Error: No data found for height scan")
        return None, None
    
    # Sort by height
    sorted_pairs = sorted(zip(heights, energies))
    heights, energies = zip(*sorted_pairs)
    heights, energies = list(heights), list(energies)
    
    # Find minimum energy
    min_idx = np.argmin(energies)
    optimal_height = heights[min_idx]
    min_energy = energies[min_idx]
    
    # With E_slab/E_molecule the plotted quantity is the ADSORPTION energy;
    # without them it is the raw total energy (curve shape identical).
    is_ads = E_slab is not None and E_molecule is not None
    ylabel = 'Adsorption Energy (eV)' if is_ads else 'Total Energy (eV)'

    # Plot
    plt.figure(figsize=(9, 5))
    plt.plot(heights, energies, 'o-', linewidth=1.8, markersize=7,
             label=f'{site}-{orientation}')
    plt.plot(optimal_height, min_energy, 'r*', markersize=18,
             label=f'Optimal: h={optimal_height:.2f} Å, E={min_energy:.3f} eV')
    if is_ads:
        plt.axhline(y=0, color='k', linestyle='--', alpha=0.3)

    plt.xlabel('TCNQ Height Above Surface (Å)', fontsize=13)
    plt.ylabel(ylabel, fontsize=13)
    plt.title(f'TCNQ height scan — {site}-{orientation}, {functional_name}', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_fig:
        figname = f'height_scan_{site}_{orientation}_{functional_name}.png'
        plt.savefig(figname, dpi=200)
        print(f"✓ Saved: {figname}")
    
    plt.show()
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Height Scan Summary - {site}-{orientation}")
    print(f"{'='*70}")
    print(f"{'Height (Å)':<15} {'Energy (eV)':<20}")
    print(f"{'-'*70}")
    for h, e in zip(heights, energies):
        print(f"{h:<15.2f} {e:<20.6f}")
    print(f"{'='*70}")
    print(f"Optimal height: {optimal_height:.3f} Å")
    print(f"Minimum energy: {min_energy:.4f} eV")
    print(f"{'='*70}")
    
    return optimal_height, min_energy

# ============================================================================
# PART 8: COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main command-line interface for surfaces.py"""
    
    parser = argparse.ArgumentParser(
        description="surfaces.py - Comprehensive utility for Tutorial 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Build bilayer graphene
  python surfaces.py --build_bilayer --stacking AB --interlayer_distance 3.30
  
  # Create distance scan for binding curve
  python surfaces.py --distance_scan --stacking AB
  
  # k-point convergence
  python surfaces.py --make_k_grid_2d --k_grid_min 4 --k_grid_max 16
  python surfaces.py --plot_k_grid_2d
  
  # Vacuum convergence
  python surfaces.py --vacuum_series
  python surfaces.py --plot_vacuum
  
  # Build metal slab
  python surfaces.py --build_slab --element Au --layers 5
  
  # Build graphene slab
  python surfaces.py --build_graphene_slab --layers 2 --size 4 4
  
  # Create slab thickness series
  python surfaces.py --slab_thickness_series --element Au
  python surfaces.py --graphene_thickness_series
  
  # Build molecule
  python surfaces.py --build_molecule --molecule benzene
  python surfaces.py --build_molecule --molecule tcnq
  
  # Place TCNQ on graphene
  python surfaces.py --place_tcnq_on_graphene --tcnq_site hollow --tcnq_orientation x --tcnq_height 2.5
  python surfaces.py --create_tcnq_adsorption_series
  
  # Height-dependent adsorption scan
  python surfaces.py --create_height_scan --tcnq_site hollow --tcnq_orientation x --height_min 2.0 --height_max 3.4
  python surfaces.py --plot_height_scan --tcnq_site hollow --tcnq_orientation x
  
  # Plot binding curve
  python surfaces.py --plot_binding_curve
  
  # Extract energy from aims.out
  python surfaces.py --extract_energy aims.out
        """
    )
    
    # === Structure building arguments ===
    parser.add_argument("--build_bilayer", action="store_true",
                       help="Build bilayer graphene structure")
    parser.add_argument("--stacking", type=str, default="AB", choices=["AA", "AB"],
                       help="Stacking type (default: AB)")
    parser.add_argument("--interlayer_distance", type=float, default=3.30,
                       help="Interlayer distance in Å (default: 3.30)")
    parser.add_argument("--vacuum", type=float, default=10.0,
                       help="Vacuum spacing in Å (default: 10.0)")
    
    # === Convergence testing arguments ===
    parser.add_argument("--make_k_grid_2d", action="store_true",
                       help="Set up k-point convergence for 2D systems")
    parser.add_argument("--plot_k_grid_2d", action="store_true",
                       help="Plot k-point convergence for 2D")
    parser.add_argument("--k_grid_min", type=int, default=4,
                       help="Minimum k-grid (default: 4)")
    parser.add_argument("--k_grid_max", type=int, default=16,
                       help="Maximum k-grid (default: 16)")
    parser.add_argument("--k_grid_step", type=int, default=2,
                       help="k-grid step (default: 2)")

    parser.add_argument("--vacuum_series", action="store_true",
                       help="Create vacuum convergence series")
    parser.add_argument("--plot_vacuum", action="store_true",
                       help="Plot vacuum convergence")

    parser.add_argument("--distance_scan", action="store_true",
                       help="Create distance scan for binding energy")
    parser.add_argument("--distance_min", type=float, default=3.0,
                       help="Minimum distance for scan (default: 3.0)")
    parser.add_argument("--distance_max", type=float, default=4.5,
                       help="Maximum distance for scan (default: 4.5)")
    parser.add_argument("--distance_step", type=float, default=0.1,
                       help="Distance step size (default: 0.1)")    
    parser.add_argument("--plot_binding_curve", action="store_true",
                       help="Plot binding energy curve")

    # === Slab and molecule building arguments ===
    parser.add_argument("--build_slab", action="store_true",
                       help="Build metal slab")
    parser.add_argument("--build_graphene_slab", action="store_true",
                       help="Build graphene slab")
    parser.add_argument("--element", type=str, default="Au",
                       help="Element for slab (default: Au)")
    parser.add_argument("--layers", type=int, default=5,
                       help="Number of layers (default: 5)")
    parser.add_argument("--size", nargs=2, type=int, default=[4, 4],
                       help="Supercell size (default: 4 4)")
    parser.add_argument("--slab_thickness_series", action="store_true",
                       help="Create slab thickness series")
    parser.add_argument("--graphene_thickness_series", action="store_true",
                       help="Create graphene slab thickness series")
    
    parser.add_argument("--build_molecule", action="store_true",
                       help="Build molecule structure")
    parser.add_argument("--molecule", type=str, default="benzene",
                       help="Molecule name (default: benzene)")
    
    # TCNQ-specific arguments
    parser.add_argument("--place_tcnq_on_graphene", action="store_true",
                       help="Place TCNQ on graphene at specific site")
    parser.add_argument("--tcnq_site", type=str, default="hollow",
                       choices=["top", "bridge", "hollow"],
                       help="TCNQ adsorption site (default: hollow)")
    parser.add_argument("--tcnq_orientation", type=str, default="x",
                       choices=["x", "y"],
                       help="TCNQ orientation (default: x)")
    parser.add_argument("--tcnq_height", type=float, default=2.5,
                       help="TCNQ height above surface in Å (default: 2.5)")
    parser.add_argument("--create_tcnq_adsorption_series", action="store_true",
                       help="Create all 6 TCNQ adsorption configurations")
    
    # Height scan arguments
    parser.add_argument("--create_height_scan", action="store_true",
                       help="Create height-dependent adsorption energy scan")
    parser.add_argument("--plot_height_scan", action="store_true",
                       help="Plot height-dependent adsorption energy curve")
    parser.add_argument("--E_slab", type=float, default=None,
                       help="Total energy of graphene slab")
    parser.add_argument("--E_molecule", type=float, default=None,
                       help="Total energy of isolated TCNQ molecule")
    parser.add_argument("--height_min", type=float, default=2.0,
                       help="Minimum height for scan (default: 2.0)")
    parser.add_argument("--height_max", type=float, default=3.4,
                       help="Maximum height for scan (default: 3.4)")
    parser.add_argument("--height_step", type=float, default=0.2,
                       help="Height step size (default: 0.2)")
    parser.add_argument("--EX_step", type=int, default=1,
                       choices=[1, 2],
                       help="EX_step (default: 1)")
    # Surface geometry argument
    parser.add_argument("--surface_geometry", type=str, 
                       default="geometry_graphene.in",
                       help="Path to surface geometry file")
    
    # === Analysis arguments ===
    parser.add_argument("--extract_energy", type=str,
                       help="Extract energy from aims.out file")
    
    args = parser.parse_args()
    
    # === Execute commands based on arguments ===
    
    if args.build_bilayer:
        build_bilayer_graphene(
            interlayer_distance=args.interlayer_distance,
            vacuum=args.vacuum,
            stacking=args.stacking
        )
    
    if args.distance_scan:
        create_distance_scan(
            stacking=args.stacking, 
            distance_range=np.arange(args.distance_min, args.distance_max + args.distance_step / 2, args.distance_step),
            vacuum=args.vacuum
        )
    
    if args.vacuum_series:
        create_vacuum_series(
            interlayer_distance=args.interlayer_distance, 
            stacking=args.stacking,
            EX_step=args.EX_step
        )

    if args.build_slab:
        build_metal_slab(
            element=args.element, 
            layers=args.layers, 
            vacuum=args.vacuum,
            size=tuple(args.size)
        )
    
    if args.build_graphene_slab:
        build_graphene_slab(
            layers=args.layers, 
            vacuum=args.vacuum, 
            size=tuple(args.size)
        )
    
    if args.slab_thickness_series:
        create_slab_thickness_series(
            element=args.element, 
            vacuum=args.vacuum,
            size=tuple(args.size)
        )
    
    if args.graphene_thickness_series:
        create_graphene_thickness_series(
            vacuum=args.vacuum,
            size=tuple(args.size)
        )
    
    if args.build_molecule:
        build_molecule(mol_name=args.molecule)
    
    if args.place_tcnq_on_graphene:
        place_tcnq_on_graphene(
            surface_geometry=args.surface_geometry,
            site=args.tcnq_site,
            orientation=args.tcnq_orientation,
            height=args.tcnq_height,
            vacuum=args.vacuum
        )
    
    if args.create_tcnq_adsorption_series:
        create_tcnq_adsorption_series(
            surface_geometry=args.surface_geometry,
            height=args.tcnq_height,
            vacuum=args.vacuum
        )
    
    if args.create_height_scan:
        height_range = np.arange(args.height_min, args.height_max + args.height_step, args.height_step)
        create_height_scan_series(
            surface_geometry=args.surface_geometry,
            site=args.tcnq_site,
            orientation=args.tcnq_orientation,
            height_range=height_range.tolist(),
            vacuum=args.vacuum
        )
    
    if args.plot_height_scan:
        plot_height_scan(
            site=args.tcnq_site,
            orientation=args.tcnq_orientation,
            E_slab=args.E_slab,
            E_molecule=args.E_molecule
        )
    
    if args.make_k_grid_2d:
        make_k_grid_2d(
            k_grid_min=args.k_grid_min, 
            k_grid_max=args.k_grid_max,
            k_grid_step=args.k_grid_step
        )
    
    if args.plot_k_grid_2d:
        plot_k_grid_2d()
    
    if args.plot_vacuum:
        plot_vacuum_convergence()
    
    if args.plot_binding_curve:
        plot_binding_curve()
    
    if args.extract_energy:
        energy = extract_total_energy(args.extract_energy)
        if energy:
            print(f"Total energy: {energy:.6f} eV")


if __name__ == "__main__":
    main()
