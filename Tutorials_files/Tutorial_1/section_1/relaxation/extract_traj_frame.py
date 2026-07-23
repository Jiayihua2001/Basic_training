from ase import Atoms
from ase.io import write

def extract_trajectory_from_aims(filename='aims.out'):
    with open(filename, 'r') as f:
        lines = f.readlines()

    trajectory = []
    recording = False
    current_coords = []
    current_symbols = []

    for line in lines:
        if "Updated atomic structure:" in line:
            if current_coords:
                atoms = Atoms(positions=current_coords, symbols=current_symbols)
                trajectory.append(atoms)
                current_coords = []
                current_symbols = []
            recording = True
            continue

        if recording:
            if line.strip().startswith("atom"):
                parts = line.strip().split()
                coords = list(map(float, parts[1:4]))
                symbol = parts[4]
                current_coords.append(coords)
                current_symbols.append(symbol)
            elif line.strip() == "":
                # End of block
                if current_coords:
                    atoms = Atoms(positions=current_coords, symbols=current_symbols)
                    trajectory.append(atoms)
                    current_coords = []
                    current_symbols = []
                recording = False

    # Catch the final frame
    if current_coords:
        atoms = Atoms(positions=current_coords, symbols=current_symbols)
        trajectory.append(atoms)

    return trajectory

if __name__ == "__main__":
    traj = extract_trajectory_from_aims('aims.out')
    if traj:
        write('trajectory.xyz', traj, format='xyz')
        print(f"Extracted {len(traj)} frames to trajectory.xyz")
    else:
        print("No frames found.")
