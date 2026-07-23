#!/usr/bin/env python3
"""
H2 Binding Energy Distance Generator

This script generates FHI-aims calculation directories for H2 molecules
at various bond distances to study binding energy curves.

Author: Generated for computational chemistry tutorial
"""

from ase import Atoms
from ase.io import write
import numpy as np
from pathlib import Path
import shutil
import sys

def create_h2_molecule(distance):
    """
    Create an H2 molecule with specified bond distance.
    
    Args:
        distance (float): H-H bond distance in Angstroms
        
    Returns:
        ase.Atoms: H2 molecule object
    """
    return Atoms(
        'H2', 
        positions=[[0, 0, 0], [0, 0, distance]], 
        cell=[6, 6, 6], 
        pbc=False
    )

def copy_file_safely(src_path, dest_path):
    """
    Copy a file with error handling.
    
    Args:
        src_path (Path): Source file path
        dest_path (Path): Destination file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        shutil.copy2(src_path, dest_path)
        return True
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error copying {src_path} to {dest_path}: {e}")
        return False

def main():
    """Main function to generate H2 binding energy calculation directories."""
    
    # File paths for required input files
    submit_path = Path("submit.sh").resolve()
    control_path = Path("control.in").resolve()
    
    # Verify required files exist
    missing_files = []
    if not submit_path.exists():
        missing_files.append(str(submit_path))
    if not control_path.exists():
        missing_files.append(str(control_path))
    
    if missing_files:
        print(f"Error: Missing required files: {', '.join(missing_files)}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path("H2_binding_energy")
    output_dir.mkdir(exist_ok=True)
    print(f"Created output directory: {output_dir}")
    
    # Bond distance range: 0.5 to 1.0 Å in steps of 0.1 Å (upper bound 1.05 so
    # the 1.0 Å endpoint is included despite float rounding), plus one wide
    # separation (6.0 Å) as the dissociation-limit reference for the bond energy
    distances = np.append(np.arange(0.5, 1.05, 0.1), 6.0)
    
    successful_dirs = 0
    total_dirs = len(distances)
    
    # Generate calculation directories for each distance
    for distance in distances:
        # Create subdirectory name with proper formatting
        sub_path = output_dir / f"H2_{distance:.1f}"
        sub_path.mkdir(exist_ok=True)
        
        # Create H2 molecule at specified distance
        h2_molecule = create_h2_molecule(distance)
        
        # Write geometry file in FHI-aims format
        geometry_file = sub_path / "geometry.in"
        write(geometry_file, h2_molecule, format='aims')
        
        # Copy required input files to calculation directory
        files_copied = 0
        files_copied += copy_file_safely(submit_path, sub_path / "submit.sh")
        files_copied += copy_file_safely(control_path, sub_path / "control.in")
        
        if files_copied == 2:
            successful_dirs += 1
            print(f"✓ Created: {sub_path} (d = {distance:.1f} Å)")
        else:
            print(f"✗ Failed: {sub_path} (file copy errors)")
    
    # Summary
    print(f"\nSummary: {successful_dirs}/{total_dirs} directories created successfully")
    if successful_dirs < total_dirs:
        print("Some directories had errors. Check file permissions and paths.")
        sys.exit(1)

if __name__ == "__main__":
    main()

