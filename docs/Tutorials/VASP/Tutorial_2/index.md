---
layout: default
parent: "VASP"
grand_parent: "Tutorials"
title: "Calculation Descriptions"
nav_order: 2
---

# Calculation Descriptions
In this section we will discus the inputs you need in order to run all the different types of calculations that we run in the Marom group.

## General Inputs
### INCAR
As stated in [VASP Basics](../Tutorial_1/), the INCAR contains the set of instructions that tells VASP what type of  calculation to perform. Although we perform many different types of calculations, there are some standard parameters that we always use. Sometimes, we may choose to alter   the following parameters slightly, but for the vast majority of our calculations, these will remain constant.

```txt
ALGO = Fast      # Mixture of Davidson and RMM-DIIS algos
PREC = Normal         # Normal precision
GGA_COMPAT = .False.    # Restore the full lattice symmetry of the GGA potential
EDIFF = 1E-6     # Convergence criteria for electronic converge
NELM = 500       # Max number of electronic steps
ENCUT = 350      # Cut off energy
LASPH = .True.     # Include non-spherical contributions from gradient corrections
BMIX = 3         # Mixing parameter for convergence
AMIN = 0.01      # Mixing parameter for convergence
SIGMA = 0.05     # Width of smearing in eV
```

> **About `EDIFF`.** From the [VASP wiki](https://www.vasp.at/wiki/index.php/EDIFF):
> "EDIFF specifies the global break condition for the electronic SC-loop." "The relaxation of the electronic degrees of freedom stops if the total (free) energy change and the band-structure-energy change ('change of eigenvalues') between two steps are both smaller than EDIFF (in eV)."
> The VASP default is `1E-4`; we tighten it to `1E-6` so that DOS, band, and especially HSE/SOC restarts inherit a well-converged charge density.

> **About `NBANDS`.** We no longer set `NBANDS` and let VASP pick its default — `max( NELECT/2 + NIONS/2 , 0.6·NELECT )` (rounded up, with magnetism / non-collinear corrections applied automatically). Override it only when you need extra empty states (e.g. unfolded bands, GW, or to silence the "too few bands" warning at high SIGMA).

### POSCAR
The POSCAR is the most user-dependent file in VASP and it defines the unit cell and exact location and element of each atom in the structure. For bulk structures, we typically get the initial structure file from <a href="https://materialsproject.org/" target="_blank">The Materials Project</a>. My preferred method is to just Google for my desired material (e.g. “InAs Materials Project”). Once you have the bulk structure, slabs or interfaces can be generated using either VaspVis or Ogre (our groups Python packages). More details about this with code examples will come later. The only calculations that require additional alterations to the POSCAR file are for an unfolded Band calculation and an OPT calculation

### POTCAR
The POTCAR is dependent on the elements used in the calculation and the order of the elements in the POSCAR. It is crucial that the order of the elements in the POTCAR match the order of the elements in the sixth line of the POSCAR. A POTCAR can be easily generated using the potcar.sh file. For example a common way to generate the POTCAR file is to use the head command to view the top lines of the POSCAR, and then use the potcar.sh file to generate the POTCAR file using the same elements shown in the 6th line of the POSCAR. To check the POTCAR you can use the grep command.

Given a POSCAR you can create the correct POTCAR using the following commands:

```bash
$ head POSCAR
In1 As1
1.0
0.000000 3.029200 3.029200
3.029200 0.000000 3.029200
3.029200 3.029200 0.000000
In As
1 1
direct
0.000000 0.000000 0.000000 In
0.750000 0.750000 0.750000 As

$ potcar.sh In As

$ grep 'TITEL' POTCAR
	TITEL = PAW_PBE In 08Apr2002
	TITEL = PAW_PBE As 22Sep2009
```

## Self-Consistent Field (SCF) Calculation
The SCF calculation will be used to generate converged CHG and CHGCAR files so they can be used to calculate the eigenvalues of the system.

### INCAR
In the INCAR there are four important parameters beyond the general parameters. The one parameter that never changes is ICHARG=2 because the SCF calculation must calculate the charge density of the system. The other three parameters can change based on your needs. Sometimes we don’t need to write the CHG* files since we only need to do the SCF calculation, or sometimes we need the WAVECAR for STM simulations or wave function visualizations. Additionally, ISMEAR=0 is the standard parameter we used, but for certain materials a different smearing method might be necessary for convergence.

```txt
ICHARG = 2 # Generate CHG* from a superposition of atomic charge densities
ISMEAR = 0 # Fermi smearing
LCHARG = .True. # Write the CHG* files
LWAVE = .False. # Does not write the WAVECAR
```

The following code can be used to generate the INCAR
```bash
incar.py --scf
or
incar.py -s
```

### KPOINTS
The KPOINTS file for an SCF calculation is one of the most basic and easy to generate  files. For the SCF calculation we use a Γ-centered Monkhorst-Pack grid of a specified density. Depending on the material, the size of the grid might change. For example, if you are working with a supercell, the k-point grid does not have to be as dense since the reciprocal lattice size is inversely proportional to the real space lattice size (i.e. large real space lattice $\rightarrow$ small reciprocal lattice $\rightarrow$ less dense grid required to fill the space)

```txt
Automatic kpoint scheme  
0  
Gamma  
7 7 7
```

To generate the KPOINTS file for a SCF calculation the kpoints.py file can be used.

```bash
kpoints.py --grid --density 7 7 7
or
kpoints.py -g -d 7 7 7
```

## Density of States (DOS) Calculation
### INCAR
In the INCAR there are eight important parameters beyond the general parameters. The only parameters that can be changed are NEDOS, EMIN, and EMAX. These values are used to determine the energy range to be calculated and how many points are included within the given energy range. By default, only 301 points are sampled for the density of states, and the energy range is unconstrained, so it includes the states with the lowest and highest energies. For the most part, we only care about a small range of energies around the Fermi energy, so we like to constrain the values between emin and emax.

```txt
ICHARG = 11     # Calculate eigenvalues from preconverged CHGCAR
ISMEAR = -5     # Tetrahedron method with Blochl corrections
LCHARG = .False.  # Does not write the CHG* files
LWAVE = .False.   # Does not write the WAVECAR files 
LORBIT = 11     # Projected data (lm-decomposed PROCAR)
NEDOS = 3001    # 3001 points are sampled for the DOS
EMIN = emin     # Minimum energy for the DOS plot
EMAX = emax     # Maximum energy for the DOS plot
```

The actual values of emin and emax can be calculated manually by finding the Fermi energy from the OUTCAR of the SCF calculation and manually determining a range based on that value. For example, if it was only necessary to observe 3 eV above and below the Fermi energy, and the Fermi energy was -1 eV, then emin=-4 and emax=2 (Note that these are absolute energy values and not relative to the Fermi energy like how it is typically plotted). There is also a way to automate the determination of these values by adding the following lines of code to your submission script in your `scf` calculation.

```bash
fermi_str=$(grep 'E-fermi' OUTCAR)  
fermi_array=($fermi_str)  
efermi=${fermi_array[2]}  
emin=`echo $efermi - 3 | bc -l`  
emax=`echo $efermi + 3 | bc -l`  
sed -i "s/EMIN[[:space:]]*=[[:space:]]*emin/EMIN = $emin/" ../dos/INCAR  
sed -i "s/EMAX[[:space:]]*=[[:space:]]*emax/EMAX = $emax/" ../dos/INCAR
```

### KPOINTS
The only difference between the KPOINTS file of a DOS calculation and that of a SCF calculation is that the grid should be denser. This is due to the fact that we want a very accurate energy evaluation for the density of states, so we choose a finer grid.

```txt
Automatic kpoint scheme  
0  
Gamma  
15 15 15
```

o generate the KPOINTS file for a DOS calculation the `kpoints.py` file can again be used.

```bash
kpoints.py --grid --density 15 15 15
or
kpoints.py -g -d 15 15 15
```

## Band Structure Calculation (Band) Calculation
In the INCAR there are five important parameters beyond the general parameters. The only parameters that can be changed are LWAVE and LORBIT. In the case of a calculation where it is desired to perform band unfolding the WAVECAR must be written (`LWAVE = .True.`). In the case where it is not important view the projected band structure (e.g. convergence tests) then the LORBIT tag can be removed.

```txt
ICHARG = 11     # Calculate eigenvalues from preconverged CHGCAR
ISMEAR = 0      # Fermi smearing
LCHARG = .False.  # Does not write the CHG* files
LWAVE = .False.   # Does not write the WAVECAR file (.True. for unfolding)
LORBIT = 11     # Projected data (lm-decomposed PROCAR)
```

To generate the INCAR for a Band calculation the `incar.py` file can be used.

```bash
incar.py --band
or
incar.py -b
```

### KPOINTS
For a band structure calculation, the KPOINTS file can take on one of three forms: regular, HSE, or unfolded. The KPOINTS file for a regular calculation is the easiest to generate since all you need to specify is the location and labels of each high symmetry point. There are a variety of different ways to find the coordinates of the high symmetry points in a Brillouin zone, but one of the more convenient methods it to use SeeK-path where you just need to upload a POSCAR to the website and it will find and visualize the high symmetry points for you. The same algorithm used by this website is also implemented in the kpoints.py file and the following KPOINTS file can be generated using the following command:

```bash
kpoints.py --band --coords GXWLGK --segments 50
or
kpoints.py -b -c GXWLGK -n 50
```

The ouput of the above for a Zinc-Blende structure such as InAs will be:

```txt
band  
50  
Line-mode  
reciprocal  
0 0 0 ! G  
0.5 0.0 0.5 ! X

0.5 0.0 0.5 ! X  
0.5 0.25 0.75 ! W 

0.5 0.25 0.75 ! W  
0.5 0.5 0.5 ! L  

0.5 0.5 0.5 ! L  
0 0 0 ! G  

0 0 0 ! G  
0.375 0.375 0.75 ! K
```

For an HSE calculation, the process is slightly more complicated since the KPOINTS must be explicitly defined and they must be appended to the end of a file from the SCF calculation that shows the coordinates of the k-points used to sample the irreducible Brillouin zone called the IBZKPT. Luckily, we have a script to easily generate this using the regular KPOINTS and IBZKPT files as inputs. Shown below are the top few lines of the HSE KPOINTS file. The lines where the 4th column is non-zero are from the IBZKPT file, and the lines where the 4th column is zero are the actual points along the k-path.

```txt
Automatically generated mesh  
129  
Reciprocal lattice  
 0.00000000000000 0.00000000000000 0.00000000000000 1  
 0.12500000000000 0.00000000000000 0.00000000000000 8  
 0.25000000000000 0.00000000000000 0.00000000000000 8  
 0.37500000000000 0.00000000000000 0.00000000000000 8  
 0.50000000000000 0.00000000000000 0.00000000000000 4  
...  
-0.37500000000000 0.37500000000000 0.12500000000000 48  
-0.25000000000000 0.37500000000000 0.12500000000000 24  
-0.37500000000000 0.50000000000000 0.12500000000000 12  
-0.25000000000000 0.50000000000000 0.25000000000000 6  
 0.00000000000000 0.00000000000000 0.00000000000000 0  
 0.02631578947368 0.00000000000000 0.02631578947368 0  
 0.05263157894737 0.00000000000000 0.05263157894737 0  
 0.07894736842105 0.00000000000000 0.07894736842105 0
```

To generate the above file, it is as simple as running the kpoints.py file with the following commands:

```bash
kpoints.py --band --hse --coords GXWLGK --ibzkpt ../scf/IBZKPT
or
kpoints.py -b -e -c GXWLGK -i ../scf/IBZKPT
```

Last, but certainly not least there is the KPOINTS file for an unfolded band structure calculation (more details about unfolding later). This is the most involved calculation to set up, but our group has developed many tools to make the setup relatively easy. The format of the KPOINTS file is similar to that of the HSE calculation because the k-points are explicitly listed, but the IBZKPT part is not shown.

```txt
kpoints generated by PYVASPWFC  
41  
Rec  
	0.00000000 -0.48333333 -0.46666667 1.0  
	0.00000000 -0.46666667 0.06666667 1.0  
	0.00000000 -0.45000000 -0.40000000 1.0  
	0.00000000 -0.43333333 0.13333333 1.0  
	0.00000000 -0.41666667 -0.33333333 1.0  
	0.00000000 -0.40000000 0.20000000 1.0  
	...
```

This file can be generated using the code below:

```python
from vaspvis.utils import generate_kpoints, convert_slab  

M = convert_slab(  
	bulk_path='POSCAR_bulk', # Path to bulk POSCAR file  
	slab_path='POSCAR_slab', # Path to slab POSCAR file  
	index=[1,1,1], # Miller indices of the surface  
	generate=False, # Does not generate a converted POSCAR  
)  
hsp = [  
	[2/3, 1/3, 1/3], # K/3  
	[0.0, 0.0, 0.0], # Gamma  
	[2/3, 1/3, 1/3], # K/3  
]  
generate_kpoints(  
	M=M, # Transformation matrix  
	high_symmetry_points=hsp, # High symmetry points  
	n=40, # Number of k-points between each high symmetry point  
	output='KPOINTS_unfolded' # Output file name  
)
```

### POSCAR
For an unfolded band structure calculation, a rotation must be applied to the lattice vectors of the unit cell in order for the transformation matrix to be an integer matrix (necessary for our unfolding code). The following code is an example of how to generate a converted POSCAR for an unfolded band structure calculation.

```python
from vaspvis.utils import generate_kpoints, convert_slab  

M = convert_slab(  
	bulk_path='POSCAR_bulk', # Path to bulk POSCAR file  
	slab_path='POSCAR_slab', # Path to slab POSCAR file  
	index=[1,1,1], # Miller indices of the surface  
	generate=False, # Does not generate a converted POSCAR  
)  
```

The output of the code will result in the following, where the difference between the tops of the regular and converted POSCAR’s can be clearly seen.

```txt
In116 As120 H4  
1.0  
4.283936 -7.419994 0.000000  
4.283936 7.419994 0.000000  
0.000000 0.000000 146.908393  
In As H  
115 116 4
```

```txt
In115 As116 H4  
1.0  
-0.000000 -6.058400 6.058400  
-6.058400 6.058400 0.000000  
-84.817600 -84.817600 -84.817600  
In As H  
115 116 4
```

## Structure Optimization (OPT)
Structural optimization calculations are mostly used to relax atoms at a surface or at an interface.

### INCAR
In the INCAR there are six important parameters beyond the general parameters. The first four parameters are essentially the same as an SCF calculation except for the fact that we typically do not write the CHG or CHGCAR files because we do not use them for anything after the OPT calculation in finished. The only parameter that can be changed is NSW which is the total number of ionic steps to be taken. Typically 50 ionic steps is more than enough, but is some cases this might need to be increased.

```txt
ICHARG = 2      # Generate CHG* from a superposition of atomic charge densities
ISMEAR = 0      # Fermi smearing
LCHARG = .False.  # Does not write the CHG* files
LWAVE = .False.   # Does not write the WAVECAR
IBRION = 2      # Ionic relaxation
NSW = 50        # Maximum of 50 ionic steps
```

To generate the INCAR for a OPT calculation the incar.py file can be used.

```bash
incar.py --opt
or
incar.py -o
```

### KPOINTS
The KPOINTS file for an OPT calculation is the same as a KPOINTS file for an SCF calculation.

### POSCAR
For a structural optimization calculation, a few changes must be made to the POSCAR file to enable what is called selective dynamics. In the 8th line “Selective dynamics” must be included in order for VASP to understand that only certain atoms should be shifted. Then, after each line with atomic coordinates, three Boolean statements (T or F) must be added to determine if the atom can shift and which Cartesian direction(s) it is confined to. An example is shown below where the pseudohydrogen positions of an InSb(110) slab are relaxed in the z-direction only and all other atoms are constrained.

```txt
In14 Sb14 H4  
1.0  
4.581628 0.000000 0.000000  
0.000000 6.479400 0.000000  
0.000000 0.000000 94.362208  
In Sb H H  
14 14 2 2  
Selective dynamics  
direct  
0.500000 0.500000 0.657799 F F F In  
0.000000 0.000000 0.633522 F F F In  
...  
0.000000 0.750000 0.657799 F F F Sb  
0.500000 0.250000 0.633522 F F F Sb  
...  
0.500000 0.386331 0.328962 F F T H  
0.000000 0.886331 0.671038 F F T H  
0.000000 0.861263 0.328728 F F T H  
0.500000 0.361263 0.671272 F F T H
```

## Adding DFT+U to a Calculation
Adding DFT+U is necessary for most calculations involving semiconductors because it corrects for the massive underestimate of the band gap with GGA. Our group has developed a method to predict the effective U value using Bayesian optimization by tuning the effective U parameters to best match the PBE+U band structure to the band structure calculated with HSE. A full example of how to run the Bayesian optimization code will be included in a following section for InAs.

### INCAR
In the INCAR there are six important parameters beyond the general parameters. The only parameters that need to be changed are the ones for LDAUL, which determine the orbitals that the U value is applied, and LDAUU, which is where the actual effective U values are entered.

```txt
LDAU = .True.       # Determines if DFT+U is used
LDAUTYPE = 2      # Dudarev formulation
LDAUL = 1 1       # l-quantum number to apply the U-value on (-1 turns it off)
LDAUU = -0.5 -7.5 # Effective U-value for each species
LDAUJ = 0.0 0.0   # J-value (Always zero for Dudarev method)
LMAXMIX = 4       # Max l-quantum number for charge density mixing
```

To generate the INCAR for a DFT+U calculation, the incar.py file can be used. Below is an example for generating an INCAR for an SCF calculation with DFT+U.

```bash
incar.py --scf --dftu
or
incar.py -s -u
```

## Adding Spin-Orbit Coupling (SOC) to a Calculation
Adding spin orbit coupling is very important for most of the materials that we study in the group because it models the spin-orbit interactions between electrons.

### INCAR
In the INCAR there are two important parameters beyond the general parameters. The only parameter that needs to change is the `MAGMOM` parameter which defines the magnetic moment for each atom in the x, y, and z directions. The example shown below is for a bulk InAs calculation where there are only two atoms in the unit cell. Since both In and As have no magnetic moment, $m_x$, $m_y$, and $m_z$ are all 0.

```txt
LSORBIT = .True.                    # Turn on spin-orbit coupling
MAGMOM = 0 0 0 0 0 0  # Set the magnetic moment for each atom (3 for each atom)
or
MAGMOM = 6*0
```

To generate the INCAR for an SOC calculation, the incar.py file can be used. Below is an example for generating an INCAR for an SCF calculation with SOC

```bash
incar.py --scf --soc
or
incar.py -s -c
```

```txt
# general 
ALGO = Fast     # Mixture of Davidson and RMM-DIIS algos
PREC = Normal        # Normal precision
GGA_COMPAT = .False.   # Restore the full lattice symmetry of the GGA potential
EDIFF = 1E-6    # Convergence criteria for electronic converge
NELM = 500      # Max number of electronic steps
ENCUT = 400     # Cut off energy
LASPH = .True.    # Include non-spherical contributions from gradient corrections
BMIX = 3        # Mixing parameter for convergence
AMIN = 0.01     # Mixing parameter for convergence 
SIGMA = 0.05    # Width of smearing in eV

# parallelization
KPAR = 8        # The number of k-points to be treated in parallel
NCORE = 1        # Auto-reset to 1 by VASP when OpenMP is enabled

# scf 
ICHARG = 2      # Generate CHG* from a superposition of atomic charge densities
ISMEAR = 0      # Fermi smearing
LCHARG = .True.   # Write the CHG* files
LWAVE = .False.   # Does not write the WAVECAR
LREAL = Auto    # Automatically chooses rea/reciprocal space for projections
```
