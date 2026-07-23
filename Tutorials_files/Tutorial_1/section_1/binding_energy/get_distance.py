from ase.io import read
ase_atoms = read("geometry.in.next_step",format="aims")
distance = ase_atoms.get_distance(0, 1)
print(f"Final H-H Distance {distance}")