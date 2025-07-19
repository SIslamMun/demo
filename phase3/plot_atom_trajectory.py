#!/usr/bin/env python3
"""
Atom Trajectory Plotting Script
Plots the 3D trajectory of a single atom over time from the nanoparticles.bp5 dataset
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from adios2 import FileReader
import argparse
import sys
import os

def plot_atom_trajectory(file_path, atom_id, output_file="atom_trajectory.png"):
    """
    Plot the trajectory of a specific atom over time
    
    Args:
        file_path: Path to the nanoparticles.bp5 file
        atom_id: ID of the atom to track (1-272)
        output_file: Output PNG file name
    """
    
    print(f"Plotting trajectory for atom {atom_id}")
    print(f"Reading data from: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return False
    
    try:
        with FileReader(file_path) as reader:
            # Get dataset info
            vars_info = reader.available_variables()
            steps_available = int(vars_info['ntimestep']['AvailableStepsCount'])
            natoms = reader.read("natoms")[0]  # Get first element
            
            print(f"Dataset has {natoms} atoms and {steps_available} timesteps")
            
            # Validate atom_id
            if atom_id < 1 or atom_id > natoms:
                print(f"Error: atom_id must be between 1 and {natoms}")
                return False
            
            # Get box dimensions for coordinate conversion
            boxxlo = reader.read("boxxlo")[0]
            boxxhi = reader.read("boxxhi")[0]
            boxylo = reader.read("boxylo")[0]
            boxyhi = reader.read("boxyhi")[0]
            boxzlo = reader.read("boxzlo")[0]
            boxzhi = reader.read("boxzhi")[0]
            
            box_dims = {
                'x': [boxxlo, boxxhi],
                'y': [boxylo, boxyhi],
                'z': [boxzlo, boxzhi]
            }
            
            print(f"Box dimensions: X=[{boxxlo:.1f}, {boxxhi:.1f}], Y=[{boxylo:.1f}, {boxyhi:.1f}], Z=[{boxzlo:.1f}, {boxzhi:.1f}] Å")
            
            # Read timesteps for time axis
            timesteps = reader.read("ntimestep", step_selection=[0, steps_available])
            physical_times = timesteps * 0.001  # Convert to picoseconds
            
            # Initialize arrays to store trajectory
            trajectory = np.zeros((steps_available, 3))
            atom_types = []
            
            print(f"Extracting trajectory for atom {atom_id}...")
            
            # Read data for each step
            for step in range(steps_available):
                if step % 10 == 0:  # Progress indicator
                    print(f"Processing step {step}/{steps_available}")
                
                # Read atoms data for this step
                atoms_data = reader.read("atoms", step_selection=[step, 1])
                atoms_data = atoms_data.reshape(int(natoms), 5)
                
                # Find the atom with the specified ID
                atom_found = False
                for i in range(int(natoms)):
                    if int(atoms_data[i, 0]) == atom_id:  # Column 0 is atom ID
                        # Get scaled coordinates (columns 2, 3, 4)
                        x_scaled = atoms_data[i, 2]
                        y_scaled = atoms_data[i, 3]
                        z_scaled = atoms_data[i, 4]
                        
                        # Convert to real coordinates
                        x_real = x_scaled * (box_dims['x'][1] - box_dims['x'][0]) + box_dims['x'][0]
                        y_real = y_scaled * (box_dims['y'][1] - box_dims['y'][0]) + box_dims['y'][0]
                        z_real = z_scaled * (box_dims['z'][1] - box_dims['z'][0]) + box_dims['z'][0]
                        
                        trajectory[step] = [x_real, y_real, z_real]
                        
                        # Store atom type (only once)
                        if step == 0:
                            atom_types.append(int(atoms_data[i, 1]))
                        
                        atom_found = True
                        break
                
                if not atom_found:
                    print(f"Warning: Atom {atom_id} not found in step {step}")
                    return False
            
            atom_type = atom_types[0] if atom_types else "Unknown"
            print(f"Atom {atom_id} is of type {atom_type}")
            
            # Calculate trajectory statistics
            total_distance = 0
            displacements = []
            for i in range(1, len(trajectory)):
                dist = np.linalg.norm(trajectory[i] - trajectory[i-1])
                total_distance += dist
                displacements.append(dist)
            
            final_displacement = np.linalg.norm(trajectory[-1] - trajectory[0])
            max_displacement = np.max(displacements) if displacements else 0
            mean_displacement = np.mean(displacements) if displacements else 0
            
            print(f"\nTrajectory Statistics:")
            print(f"  Total path length: {total_distance:.3f} Å")
            print(f"  Final displacement: {final_displacement:.3f} Å")
            print(f"  Maximum step displacement: {max_displacement:.3f} Å")
            print(f"  Mean step displacement: {mean_displacement:.3f} Å")
            
            # Create the plot
            fig = plt.figure(figsize=(15, 12))
            
            # 3D trajectory plot
            ax1 = fig.add_subplot(221, projection='3d')
            ax1.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 
                    'b-', linewidth=1.5, alpha=0.7, label='Trajectory')
            ax1.scatter(trajectory[0, 0], trajectory[0, 1], trajectory[0, 2], 
                       c='green', s=100, marker='o', label='Start')
            ax1.scatter(trajectory[-1, 0], trajectory[-1, 1], trajectory[-1, 2], 
                       c='red', s=100, marker='s', label='End')
            
            ax1.set_xlabel('X Position (Å)')
            ax1.set_ylabel('Y Position (Å)')
            ax1.set_zlabel('Z Position (Å)')
            ax1.set_title(f'3D Trajectory of Atom {atom_id} (Type {atom_type})')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # X-Y projection
            ax2 = fig.add_subplot(222)
            ax2.plot(trajectory[:, 0], trajectory[:, 1], 'b-', linewidth=1.5, alpha=0.7)
            ax2.scatter(trajectory[0, 0], trajectory[0, 1], c='green', s=100, marker='o', label='Start')
            ax2.scatter(trajectory[-1, 0], trajectory[-1, 1], c='red', s=100, marker='s', label='End')
            ax2.set_xlabel('X Position (Å)')
            ax2.set_ylabel('Y Position (Å)')
            ax2.set_title('X-Y Projection')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.axis('equal')
            
            # Time series of coordinates
            ax3 = fig.add_subplot(223)
            ax3.plot(physical_times, trajectory[:, 0], 'r-', label='X', linewidth=1.5)
            ax3.plot(physical_times, trajectory[:, 1], 'g-', label='Y', linewidth=1.5)
            ax3.plot(physical_times, trajectory[:, 2], 'b-', label='Z', linewidth=1.5)
            ax3.set_xlabel('Time (ps)')
            ax3.set_ylabel('Position (Å)')
            ax3.set_title('Coordinate Time Series')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Distance from origin over time
            ax4 = fig.add_subplot(224)
            distances_from_origin = np.linalg.norm(trajectory, axis=1)
            ax4.plot(physical_times, distances_from_origin, 'purple', linewidth=2)
            ax4.set_xlabel('Time (ps)')
            ax4.set_ylabel('Distance from Origin (Å)')
            ax4.set_title('Distance from Origin vs Time')
            ax4.grid(True, alpha=0.3)
            
            # Add overall title
            fig.suptitle(f'Trajectory Analysis: Atom {atom_id} (Type {atom_type})\n' + 
                        f'Total Path: {total_distance:.2f} Å, Final Displacement: {final_displacement:.2f} Å',
                        fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            # Save the plot
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"\nTrajectory plot saved to: {output_file}")
            
            # Also save trajectory data
            data_file = output_file.replace('.png', '_data.txt')
            with open(data_file, 'w') as f:
                f.write(f"# Trajectory data for Atom {atom_id} (Type {atom_type})\n")
                f.write(f"# Time(ps)\tX(Å)\tY(Å)\tZ(Å)\tDistance_from_origin(Å)\n")
                for i in range(len(trajectory)):
                    dist_from_origin = np.linalg.norm(trajectory[i])
                    f.write(f"{physical_times[i]:.3f}\t{trajectory[i,0]:.6f}\t{trajectory[i,1]:.6f}\t{trajectory[i,2]:.6f}\t{dist_from_origin:.6f}\n")
            
            print(f"Trajectory data saved to: {data_file}")
            
            return True
            
    except Exception as e:
        print(f"Error plotting trajectory: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Plot atom trajectory from nanoparticles.bp5 dataset')
    parser.add_argument('--atom_id', type=int, default=1, 
                       help='ID of the atom to track (1-272)')
    parser.add_argument('--input', type=str, 
                       default='/mnt/common/jcernudagarcia/demo/phase3/data/nanoparticles.bp5',
                       help='Path to nanoparticles.bp5 file')
    parser.add_argument('--output', type=str, default='atom_trajectory.png',
                       help='Output PNG file name')
    
    args = parser.parse_args()
    
    success = plot_atom_trajectory(args.input, args.atom_id, args.output)
    
    if success:
        print("\nTrajectory plotting completed successfully!")
        return 0
    else:
        print("\nTrajectory plotting failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())