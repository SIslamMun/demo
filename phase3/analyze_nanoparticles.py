#!/usr/bin/env python3
"""
LAMMPS Nanoparticles BP5 Dataset Analysis Script
Analyzes graphene oxide nanoparticle simulation data from ADIOS2 BP5 format
"""

import numpy as np
from adios2 import FileReader
import os
import sys

def analyze_nanoparticles_bp5(file_path):
    """Analyze the nanoparticles.bp5 dataset"""
    
    print("="*60)
    print("LAMMPS GO-Nanoparticle Dataset Analysis")
    print("="*60)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    analysis_results = {}
    
    try:
        with FileReader(file_path) as reader:
            print(f"Successfully opened: {file_path}")
            print()
            
            # Get available variables
            vars_info = reader.available_variables()
            print("Available Variables:")
            print("-" * 40)
            
            for name, info in vars_info.items():
                print(f"Variable: {name}")
                for key, value in info.items():
                    print(f"  {key}: {value}")
                print()
            
            analysis_results['variables'] = vars_info
            
            # Read basic simulation parameters
            print("Simulation Parameters:")
            print("-" * 40)
            
            # Number of atoms
            natoms = reader.read("natoms")
            print(f"Total number of atoms: {natoms}")
            analysis_results['natoms'] = int(natoms)
            
            # Number of columns in atoms array
            ncolumns = reader.read("ncolumns")
            print(f"Number of columns in atoms array: {ncolumns}")
            analysis_results['ncolumns'] = int(ncolumns)
            
            # Box dimensions
            boxxlo = reader.read("boxxlo")
            boxxhi = reader.read("boxxhi")
            boxylo = reader.read("boxylo")  
            boxyhi = reader.read("boxyhi")
            boxzlo = reader.read("boxzlo")
            boxzhi = reader.read("boxzhi")
            
            box_dims = {
                'x': [float(boxxlo), float(boxxhi)],
                'y': [float(boxylo), float(boxyhi)], 
                'z': [float(boxzlo), float(boxzhi)]
            }
            
            print(f"Simulation box dimensions:")
            print(f"  X: [{box_dims['x'][0]:.2f}, {box_dims['x'][1]:.2f}] Å")
            print(f"  Y: [{box_dims['y'][0]:.2f}, {box_dims['y'][1]:.2f}] Å")
            print(f"  Z: [{box_dims['z'][0]:.2f}, {box_dims['z'][1]:.2f}] Å")
            
            box_volume = ((box_dims['x'][1] - box_dims['x'][0]) * 
                         (box_dims['y'][1] - box_dims['y'][0]) * 
                         (box_dims['z'][1] - box_dims['z'][0]))
            print(f"  Box volume: {box_volume:.2f} Å³")
            
            analysis_results['box_dimensions'] = box_dims
            analysis_results['box_volume'] = box_volume
            
            # Number of processors used
            nprocs = reader.read("nprocs")
            print(f"Number of processors: {nprocs}")
            analysis_results['nprocs'] = int(nprocs)
            
            # Get number of steps
            steps_available = int(vars_info['ntimestep']['AvailableStepsCount'])
            print(f"Number of simulation steps available: {steps_available}")
            analysis_results['total_steps'] = steps_available
            
            print()
            
            # Temporal analysis
            print("Temporal Analysis:")
            print("-" * 40)
            
            # Read all timesteps
            timesteps = reader.read("ntimestep", step_selection=[0, steps_available])
            print(f"Timestep range: {timesteps[0]} to {timesteps[-1]}")
            print(f"Timestep increment: {timesteps[1] - timesteps[0] if len(timesteps) > 1 else 'N/A'}")
            
            # Convert timesteps to physical time (1 fs = 0.001 ps per timestep)
            physical_times = timesteps * 0.001  # Convert to picoseconds
            print(f"Physical time range: {physical_times[0]:.3f} to {physical_times[-1]:.3f} ps")
            print(f"Total simulation duration: {physical_times[-1] - physical_times[0]:.3f} ps")
            
            analysis_results['timesteps'] = timesteps.tolist()
            analysis_results['physical_times'] = physical_times.tolist()
            
            print()
            
            # Analyze atom types and structure
            print("Structural Analysis:")
            print("-" * 40)
            
            # Read atoms data for first and last step to analyze structure
            try:
                # First step
                atoms_first = reader.read("atoms", step_selection=[0, 1])
                atoms_first = atoms_first.reshape(int(natoms), int(ncolumns))
                
                # Last step  
                atoms_last = reader.read("atoms", step_selection=[steps_available-1, 1])
                atoms_last = atoms_last.reshape(int(natoms), int(ncolumns))
                
                # Analyze atom types
                atom_types_first = atoms_first[:, 1].astype(int)
                unique_types, type_counts = np.unique(atom_types_first, return_counts=True)
                
                print("Atom type distribution:")
                for atype, count in zip(unique_types, type_counts):
                    print(f"  Type {atype}: {count} atoms")
                
                analysis_results['atom_types'] = {
                    'types': unique_types.tolist(),
                    'counts': type_counts.tolist()
                }
                
                # Convert scaled coordinates to real coordinates for analysis
                def scaled_to_real(scaled_coords, box_dims):
                    """Convert scaled coordinates (0-1) to real coordinates"""
                    real_coords = np.zeros_like(scaled_coords)
                    real_coords[:, 0] = scaled_coords[:, 0] * (box_dims['x'][1] - box_dims['x'][0]) + box_dims['x'][0]
                    real_coords[:, 1] = scaled_coords[:, 1] * (box_dims['y'][1] - box_dims['y'][0]) + box_dims['y'][0] 
                    real_coords[:, 2] = scaled_coords[:, 2] * (box_dims['z'][1] - box_dims['z'][0]) + box_dims['z'][0]
                    return real_coords
                
                # Analyze coordinates (columns 2, 3, 4 are x, y, z scaled coordinates)
                coords_first_scaled = atoms_first[:, 2:5]
                coords_last_scaled = atoms_last[:, 2:5]
                
                coords_first_real = scaled_to_real(coords_first_scaled, box_dims)
                coords_last_real = scaled_to_real(coords_last_scaled, box_dims)
                
                # Calculate center of mass displacement
                com_first = np.mean(coords_first_real, axis=0)
                com_last = np.mean(coords_last_real, axis=0)
                com_displacement = np.linalg.norm(com_last - com_first)
                
                print(f"\nCenter of mass analysis:")
                print(f"  Initial COM: [{com_first[0]:.3f}, {com_first[1]:.3f}, {com_first[2]:.3f}] Å")
                print(f"  Final COM: [{com_last[0]:.3f}, {com_last[1]:.3f}, {com_last[2]:.3f}] Å")
                print(f"  COM displacement: {com_displacement:.3f} Å")
                
                # Calculate atomic displacement
                atom_displacements = np.linalg.norm(coords_last_real - coords_first_real, axis=1)
                max_displacement = np.max(atom_displacements)
                mean_displacement = np.mean(atom_displacements)
                
                print(f"\nAtomic displacement analysis:")
                print(f"  Maximum atomic displacement: {max_displacement:.3f} Å")
                print(f"  Mean atomic displacement: {mean_displacement:.3f} Å")
                
                analysis_results['displacement_analysis'] = {
                    'com_initial': com_first.tolist(),
                    'com_final': com_last.tolist(), 
                    'com_displacement': float(com_displacement),
                    'max_atomic_displacement': float(max_displacement),
                    'mean_atomic_displacement': float(mean_displacement)
                }
                
            except Exception as e:
                print(f"Could not analyze atoms data: {e}")
                print("This is expected for large datasets - atoms variable too large for direct access")
            
            print()
            
            # Data storage analysis
            print("Data Storage Analysis:")
            print("-" * 40)
            print(f"Dataset format: ADIOS2 BP5")
            print(f"Data dumps frequency: Every 1000 timesteps (every 1 ps)")
            print(f"Coordinate format: Scaled coordinates (0-1 range)")
            print(f"Total data points: {int(natoms) * steps_available} atom records")
            
            analysis_results['storage_info'] = {
                'format': 'ADIOS2 BP5',
                'dump_frequency': '1000 timesteps (1 ps)',
                'coordinate_format': 'Scaled (0-1 range)',
                'total_atom_records': int(natoms) * steps_available
            }
            
            print()
            
    except Exception as e:
        print(f"Error analyzing dataset: {e}")
        return None
    
    return analysis_results

def main():
    """Main analysis function"""
    
    # Path to the nanoparticles dataset
    dataset_path = "/mnt/common/jcernudagarcia/demo/phase3/data/nanoparticles.bp5"
    
    # Perform analysis
    results = analyze_nanoparticles_bp5(dataset_path)
    
    if results:
        print("Analysis completed successfully!")
        print("\nKey findings:")
        print(f"- Dataset contains {results['natoms']} atoms across {results['total_steps']} timesteps")
        print(f"- Simulation covers {results['physical_times'][-1]:.1f} ps of molecular dynamics")
        print(f"- System contains {len(results['atom_types']['types'])} different atom types")
        print(f"- Simulation box volume: {results['box_volume']:.1f} Å³")
        
        if 'displacement_analysis' in results:
            print(f"- Center of mass moved {results['displacement_analysis']['com_displacement']:.3f} Å")
            print(f"- Mean atomic displacement: {results['displacement_analysis']['mean_atomic_displacement']:.3f} Å")
    else:
        print("Analysis failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())