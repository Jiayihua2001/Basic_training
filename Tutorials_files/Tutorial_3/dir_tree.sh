#!/bin/bash

# Simple Tutorial 3 Directory Structure Setup
# Creates essential directories based on tutorial navigation

echo "Setting up Tutorial 3 directory structure..."

# EX1: Bilayer Graphene directories (based on tutorial navigation)
echo "Creating bilayer graphene directories..."
mkdir -p bilayer_graphene/convergence
mkdir -p bilayer_graphene/convergence/k_grid
mkdir -p bilayer_graphene/convergence/vacuum
mkdir -p bilayer_graphene/stacking
mkdir -p bilayer_graphene/stacking/AA
mkdir -p bilayer_graphene/stacking/AB
mkdir -p bilayer_graphene/stacking/AA/distance_scan/pbe/monolayer
mkdir -p bilayer_graphene/stacking/AA/distance_scan/pbe_ts/monolayer
mkdir -p bilayer_graphene/stacking/AA/distance_scan/pbe_mbd/monolayer
mkdir -p bilayer_graphene/stacking/AB/distance_scan/pbe/monolayer
mkdir -p bilayer_graphene/stacking/AB/distance_scan/pbe_ts/monolayer
mkdir -p bilayer_graphene/stacking/AB/distance_scan/pbe_mbd/monolayer
mkdir -p bilayer_graphene/stacking/AA/band
mkdir -p bilayer_graphene/stacking/AB/band
# EX2: TCNQ Adsorption directories
echo "Creating TCNQ adsorption directories..."
mkdir -p tcnq_adsorption/convergence
mkdir -p tcnq_adsorption/convergence/vacuum
mkdir -p tcnq_adsorption/convergence/k_grid

mkdir -p tcnq_adsorption/PBE
mkdir -p tcnq_adsorption/PBE/molecule_ref
mkdir -p tcnq_adsorption/PBE/slab_ref
mkdir -p tcnq_adsorption/PBE/adsorption_sites
mkdir -p tcnq_adsorption/PBE/adsorption_sites/topx
mkdir -p tcnq_adsorption/PBE/adsorption_sites/topy
mkdir -p tcnq_adsorption/PBE/adsorption_sites/bridgex
mkdir -p tcnq_adsorption/PBE/adsorption_sites/bridgey
mkdir -p tcnq_adsorption/PBE/adsorption_sites/hollowx
mkdir -p tcnq_adsorption/PBE/adsorption_sites/hollowy

mkdir -p tcnq_adsorption/PBE_MBD
mkdir -p tcnq_adsorption/PBE_MBD/molecule_ref
mkdir -p tcnq_adsorption/PBE_MBD/slab_ref
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites/topx
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites/topy
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites/bridgex
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites/bridgey
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites/hollowx
mkdir -p tcnq_adsorption/PBE_MBD/adsorption_sites/hollowy

mkdir -p tcnq_adsorption/PBE_TS
mkdir -p tcnq_adsorption/PBE_TS/molecule_ref
mkdir -p tcnq_adsorption/PBE_TS/slab_ref
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites/topx
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites/topy
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites/bridgex
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites/bridgey
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites/hollowx
mkdir -p tcnq_adsorption/PBE_TS/adsorption_sites/hollowy



