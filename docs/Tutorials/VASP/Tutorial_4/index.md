---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Bulk InAs (PBE+SOC)"
nav_order: 4
---

# Bulk InAs (PBE+SOC)
In this step we will run our second calculation on bulk InAs where we add in spin-orbit couple to make our calculation more accurate.

## Folder Layout
- `basic_training`
	- `InAs_bulk`
		- `pbe-soc`
			- `scf`
			- `band`
			- `dos`

## Basic Steps
1. Run the SCF Calculations in the `scf` folder.
2. Copy the CHG and CHGCAR files to the `band` and `dos` folders.
3. Run the Band and DOS calculations.
4. Plot the data.

## Global Files
The POSCAR and POTCAR will be the same for the SCF, DOS, and Band calculations.

### POSCAR
The POSCAR for the bulk InAs is given below

```txt
In1 As1  
1.0  
0.000000 3.029200 3.029200  
3.029200 0.000000 3.029200  
3.029200 3.029200 0.000000  
In As  
1 1  
direct  
0.000000 0.000000 0.000000 In  
0.250000 0.250000 0.250000 As
```

### POTCAR
The POTCAR can be easily generated using the potcar.sh script included in the basic training files.

```bash
potcar.sh In As
```

To double check the elements in the POTCAR you can run the following command

```bash
grep 'TITEL' POTCAR
```

The output will be the following

```txt
TITEL = PAW_PBE In 08Apr2002  
TITEL = PAW_PBE As 22Sep2009
```

## Automation
This entire calculation can be automated using a simple python script included below:
```python
from os.path import isdir, join
import os
import shutil

dirs = ["scf", "dos", "band"]
base_dir = os.getcwd()

for d in dirs:
    print(d)

    if not isdir(d):
        os.mkdir(d)

    shutil.copy("POSCAR", join(d, "POSCAR"))

    os.chdir(d)
    os.system(f"incar.py --{d} -c --kpar 8 --ncore 8")
    os.system("potcar.sh In As")

    if d == "scf":
        os.system("kpoints.py -g -d 7 7 7")
    elif d == "dos":
        os.system("kpoints.py -g -d 15 15 15")
    elif d == "band":
        os.system("kpoints.py -b -c GXWLGK")

    os.chdir(base_dir)
```

And it can be submitted to the cluster using the following script.

```bash
#!/bin/bash -l
#SBATCH -J pbe-soc # Job name
#SBATCH -N 1  # Number of nodes
#SBATCH -o stdout # File to which STDOUT will be written %j is the job #
#SBATCH -t 30
#SBATCH -q debug
#SBATCH -A m3578
#SBATCH --constraint=knl
export OMP_NUM_THREADS=1
module load vasp/5.4.4-knl

cd scf
srun -n 64 -c 4 --cpu_bind=cores vasp_ncl > vasp.out

fermi_str=$(grep 'E-fermi' OUTCAR)  
fermi_array=($fermi_str)  
efermi=${fermi_array[2]}  
emin=`echo $efermi - 7 | bc -l`  
emax=`echo $efermi + 7 | bc -l`  
sed -i "s/EMIN = emin/EMIN = $emin/" ../dos/INCAR  
sed -i "s/EMAX = emax/EMAX = $emax/" ../dos/INCAR

cp CHG* ../band
cp CHG* ../dos

cd ../band
srun -n 64 -c 4 --cpu_bind=cores vasp_ncl > vasp.out

cd ../dos
srun -n 64 -c 4 --cpu_bind=cores vasp_ncl > vasp.out
```

## SCF Calculation
The first step in any calculation is to perform the SCF calculation. In this section, the process to set up the input files will be shown. For a more detailed breakdown of the SCF calculation see [Calculation Descriptions](../Tutorial_2/).

### INCAR
As shown in section [Calculation Descriptions](../Tutorial_2/) the INCAR for an SCF calculation can be generated using the incar.py file.

```bash
incar.py --scf --soc
or
incar.py -s -c
```

This results in the following file.

```txt
# general
ALGO = Fast     # Mixture of Davidson and RMM-DIIS algos
PREC = N        # Normal precision
GGA_COMPAT = .FALSE.   # Restore the full lattice symmetry of the GGA potential
EDIFF = 1E-6    # Convergence criteria for electronic converge
NELM = 500      # Max number of electronic steps
ENCUT = 400     # Cut off energy
LASPH = True    # Include non-spherical contributions from gradient corrections
BMIX = 3        # Mixing parameter for convergence
AMIN = 0.01     # Mixing parameter for convergence
SIGMA = 0.05    # Width of smearing in eV

# parallelization
KPAR = 8        # The number of k-points to be treated in parallel
NCORE = 8        # The number of bands to be treated in parallel

# scf
ICHARG = 2      # Generate CHG* from a superposition of atomic charge densities
ISMEAR = 0      # Fermi smearing
LCHARG = True   # Write the CHG* files
LWAVE = False   # Does not write the WAVECAR
LREAL = Auto    # Automatically chooses real/reciprocal space for projections

# soc 
LSORBIT = True  # Turn on spin-orbit coupling
MAGMOM = 6*0 # Set the magnetic moment for each atom (3 for each atom)
```

## Density of States Calculation
After the SCF calculation is finished, the CHG and CHGCAR files can be copied to the folder with the DOS calculation files. For a more detailed breakdown of the DOS calculation see section [Calculation Descriptions](../Tutorial_2/).

### INCAR
The INCAR for a DOS calculation can be generated using the incar.py file.

```bash
incar.py --dos --soc
or
incar.py -d -c
```

Which results in the following file. The values of EMIN and EMAX were automatically  determined using the code shown in section [Calculation Descriptions](../Tutorial_2/).

```txt
# general 
ALGO = Fast     # Mixture of Davidson and RMM-DIIS algos
PREC = N        # Normal precision
GGA_COMPAT = .FALSE.   # Restore the full lattice symmetry of the GGA potential
EDIFF = 1E-6    # Convergence criteria for electronic converge
NELM = 500      # Max number of electronic steps
ENCUT = 400     # Cut off energy
LASPH = True    # Include non-spherical contributions from gradient corrections
BMIX = 3        # Mixing parameter for convergence
AMIN = 0.01     # Mixing parameter for convergence 
SIGMA = 0.05    # Width of smearing in eV

# parallelization
KPAR = 8        # The number of k-points to be treated in parallel
NCORE = 8        # The number of bands to be treated in parallel

# dos 
ICHARG = 11     # Calculate eigenvalues from preconverged CHGCAR
ISMEAR = -5     # Tetrahedron method with Blochl corrections
LCHARG = False  # Does not write the CHG* files
LWAVE = False   # Does not write the WAVECAR files 
LORBIT = 11     # Projected data (lm-decomposed PROCAR)
NEDOS = 3001    # 3001 points are sampled for the DOS
EMIN = -3.7174     # Minimum energy for the DOS plot
EMAX = 10.2826     # Maximum energy for the DOS plot

# soc 
LSORBIT = True  # Turn on spin-orbit coupling
MAGMOM = 6*0 # Set the magnetic moment for each atom (3 for each atom)
```

### KPOINTS
For a DOS calculation we would like to have a denser kpoint mesh to get more accurate results. The code to generate the KPOINTS file is shown below.

```bash
kpoints.py --grid --density 15 15 15
or
kpoints.py -g -d 15 15 15
```

### Results
Same vaspvis calls as the PBE run — the SOC weights are picked up automatically from the noncollinear `PROCAR`:

```python
from vaspvis.standard import dos_plain, dos_spd

dos_plain(folder='dos', output='dos_plain.png')
dos_spd(folder='dos',   output='dos_spd.png',   orbitals='spd')
```

![pbe_dos](../../../images/vasp/pbe-soc_dos_plot.png)

## Band Structure Calculation
After the SCF calculation is finished, the CHG and CHGCAR files can be copied to the folder with the Band calculation files. For a more detailed breakdown of the Band calculation see section [Calculation Descriptions](../Tutorial_2/).

### INCAR
The INCAR for a band structure calculation can be generated using the incar.py file.

```bash
incar.py --band --soc
or
incar.py -b -c
```

Which results in the following file:

```txt
# general 
ALGO = Fast     # Mixture of Davidson and RMM-DIIS algos
PREC = N        # Normal precision
GGA_COMPAT = .FALSE.   # Restore the full lattice symmetry of the GGA potential
EDIFF = 1E-6    # Convergence criteria for electronic converge
NELM = 500      # Max number of electronic steps
ENCUT = 400     # Cut off energy
LASPH = True    # Include non-spherical contributions from gradient corrections
BMIX = 3        # Mixing parameter for convergence
AMIN = 0.01     # Mixing parameter for convergence 
SIGMA = 0.05    # Width of smearing in eV

# parallelization
KPAR = 8        # The number of k-points to be treated in parallel
NCORE = 8        # The number of bands to be treated in parallel

# band 
ICHARG = 11     # Calculate eigenvalues from preconverged CHGCAR
ISMEAR = 0      # Fermi smearing
LCHARG = False  # Does not write the CHG* files
LWAVE = False   # Does not write the WAVECAR files (True for unfolding)
LORBIT = 11     # Projected data (lm-decomposed PROCAR)

# soc 
LSORBIT = True  # Turn on spin-orbit coupling
MAGMOM = 6*0 # Set the magnetic moment for each atom (3 for each atom)
```

### KPOINTS
For a band structure calculation, the KPOINTS file is the most important input because it determines the path of your band structure. Usually we find the path from literature or helpful tools such as <a href="https://www.materialscloud.org/work/tools/seekpath" target="_blank">SeeK-path</a>. For our zinc-blende structures such as InAs we choose the k-path $\Gamma-X-W-L-\Gamma-K$, which can be generated using the following code with `kpoints.py`.

```bash
kpoints.py --band --coords GXWLGK
or
kpoints.py -b -c GXWLGK
```

The resulting KPOINTS file will look like this:

```txt
Line_mode KPOINTS file
50
Line_mode
Reciprocal
0.0 0.0 0.0 ! G
0.5 0.0 0.5 ! X

0.5 0.0 0.5 ! X
0.5 0.25 0.75 ! W

0.5 0.25 0.75 ! W
0.5 0.5 0.5 ! L

0.5 0.5 0.5 ! L
0.0 0.0 0.0 ! G

0.0 0.0 0.0 ! G
0.375 0.375 0.75 ! K
```

### Results
And the band structure:

```python
from vaspvis.standard import band_plain, band_spd

band_plain(folder='band', output='band_plain.png')
band_spd(folder='band',   output='band_spd.png')
```

![pbe_band_structure](../../../images/vasp/pbe-soc_bands_plot.png)

## Concluding Notes
Some things to note about the results:
- This calculation was a bit slower than the calculation without PBE. It took about 35 seconds for the SCF calculation, 30 seconds for the band calculation, and 30 seconds for the DOS calculation using 1 node on the NERSC Cori machine. 
- PBE+SOC is still predicting InAs to be a metal (no band gap) even though we know from experiments that is it a small band gap semiconductor with a band gap of ~0.35 eV.
	- This is a common error for DFT as it underestimates the band gap due to the self interaction error. We will look at ways to fix this this in future calculation.
	- SOC can usually increase the size of the band gap, but for small band gap semiconductors, just adding SOC isn't enough.
