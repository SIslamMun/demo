#!/usr/bin/env python3
"""
Plot atom trajectory from LAMMPS ADIOS2 BP5 dataset
This script extracts and visualizes the 3D trajectory of a specific atom over time.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from adios2 import FileReader
import argparse
import sys

def convert_scaled_to_real_coordinates(scaled_coords, box_params):
    """
    Convert scaled coordinates (0-1) to real coordinates using box dimensions
    
    Args:
        scaled_coords: numpy array of scaled coordinates [x, y, z]
        box_params: dict with box dimensions
    
    Returns:
        numpy array of real coordinates in Angstroms
    """
    real_coords = np.zeros_like(scaled_coords)
    
    # x_real = x_scaled * (boxxhi - boxxlo) + boxxlo
    real_coords[:, 0] = scaled_coords[:, 0] * (box_params['boxxhi'] - box_params['boxxlo']) + box_params['boxxlo']
    # y_real = y_scaled * (boxyhi - boxylo) + boxylo  
    real_coords[:, 1] = scaled_coords[:, 1] * (box_params['boxyhi'] - box_params['boxylo']) + box_params['boxylo']
    # z_real = z_scaled * (boxzhi - boxzlo) + boxzlo
    real_coords[:, 2] = scaled_coords[:, 2] * (box_params['boxzhi'] - box_params['boxzlo']) + box_params['boxzlo']
    
    return real_coords

def get_atom_trajectory(bp_file_path, atom_id):
    """
    Extract trajectory data for a specific atom from the ADIOS2 dataset
    
    Args:
        bp_file_path: Path to the BP5 file
        atom_id: ID of the atom to track (1-indexed as in LAMMPS)
    
    Returns:
        dict with trajectory data including coordinates, times, and metadata
    """
    trajectory_data = {
        'atom_id': atom_id,
        'timestamps': [],
        'timesteps': [],
        'scaled_coords': [],
        'real_coords': [],
        'atom_type': None,
        'box_params': {},
        'error': None
    }
    
    try:
        with FileReader(bp_file_path) as reader:
            # Get box parameters (assuming they're constant)
            variables = reader.available_variables()
            
            # Read box dimensions from first step
            for box_var in ['boxxlo', 'boxxhi', 'boxylo', 'boxyhi', 'boxzlo', 'boxzhi']:
                if box_var in variables:
                    box_val = reader.read(box_var, step_selection=[0, 1])
                    trajectory_data['box_params'][box_var] = float(box_val[0]) if box_val.ndim > 0 else float(box_val)
            
            # Get total number of steps
            if 'ntimestep' in variables:
                steps_count = int(variables['ntimestep']['AvailableStepsCount'])
            else:
                steps_count = int(variables['atoms']['AvailableStepsCount'])
            
            print(f"Reading trajectory for atom {atom_id} across {steps_count} steps...")
            
            # Read data step by step to find the atom
            for step in range(steps_count):
                try:
                    # Read atoms data for this step
                    atoms_data = reader.read("atoms", step_selection=[step, 1])
                    timestep = reader.read("ntimestep", step_selection=[step, 1])
                    
                    if atoms_data is not None and atoms_data.size > 0:
                        # Reshape if needed (sometimes ADIOS returns flattened arrays)
                        if atoms_data.ndim == 1:
                            atoms_data = atoms_data.reshape(-1, 5)
                        
                        # Find the atom with the specified ID
                        atom_indices = np.where(atoms_data[:, 0] == atom_id)[0]
                        
                        if len(atom_indices) > 0:
                            atom_idx = atom_indices[0]
                            atom_row = atoms_data[atom_idx]
                            
                            # Store atom type (should be constant)
                            if trajectory_data['atom_type'] is None:
                                trajectory_data['atom_type'] = int(atom_row[1])
                            
                            # Store scaled coordinates
                            scaled_coord = atom_row[2:5]  # x, y, z scaled coordinates
                            trajectory_data['scaled_coords'].append(scaled_coord)
                            
                            # Store timestep
                            current_timestep = int(timestep[0]) if timestep.ndim > 0 else int(timestep)
                            trajectory_data['timesteps'].append(current_timestep)
                            
                            # Convert to time in picoseconds (1 fs timestep)
                            time_ps = current_timestep * 0.001  # Convert fs to ps
                            trajectory_data['timestamps'].append(time_ps)
                        else:
                            print(f"Warning: Atom {atom_id} not found in step {step}")
                    
                except Exception as e:
                    print(f"Error reading step {step}: {e}")
                    continue
            
            # Convert to numpy arrays
            if trajectory_data['scaled_coords']:
                trajectory_data['scaled_coords'] = np.array(trajectory_data['scaled_coords'])
                trajectory_data['timestamps'] = np.array(trajectory_data['timestamps'])
                trajectory_data['timesteps'] = np.array(trajectory_data['timesteps'])
                
                # Convert to real coordinates
                trajectory_data['real_coords'] = convert_scaled_to_real_coordinates(
                    trajectory_data['scaled_coords'], 
                    trajectory_data['box_params']
                )
                
                print(f"Successfully extracted trajectory for atom {atom_id}")
                print(f"Atom type: {trajectory_data['atom_type']}")
                print(f"Number of trajectory points: {len(trajectory_data['timestamps'])}")
            else:
                trajectory_data['error'] = f"No trajectory data found for atom {atom_id}"
                
    except Exception as e:
        trajectory_data['error'] = f"Error reading trajectory: {str(e)}"
    
    return trajectory_data

def plot_atom_trajectory(trajectory_data, output_file):
    """
    Create a comprehensive plot of the atom trajectory
    
    Args:
        trajectory_data: Dict containing trajectory information
        output_file: Path for output PNG file
    """
    if trajectory_data['error']:
        print(f"Error: {trajectory_data['error']}")
        return
    
    if len(trajectory_data['real_coords']) == 0:
        print("No trajectory data to plot")
        return
    
    coords = trajectory_data['real_coords']
    times = trajectory_data['timestamps']
    atom_id = trajectory_data['atom_id']
    atom_type = trajectory_data['atom_type']
    
    # Create a figure with multiple subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 3D trajectory plot
    ax1 = fig.add_subplot(2, 3, 1, projection='3d')
    
    # Create a color map based on time
    colors = plt.cm.viridis(np.linspace(0, 1, len(coords)))
    
    # Plot the trajectory with color gradient
    for i in range(len(coords)-1):
        ax1.plot([coords[i, 0], coords[i+1, 0]], 
                [coords[i, 1], coords[i+1, 1]], 
                [coords[i, 2], coords[i+1, 2]], 
                color=colors[i], linewidth=1.5, alpha=0.7)
    
    # Mark start and end points
    ax1.scatter(coords[0, 0], coords[0, 1], coords[0, 2], 
               c='green', s=100, marker='o', label='Start')
    ax1.scatter(coords[-1, 0], coords[-1, 1], coords[-1, 2], 
               c='red', s=100, marker='s', label='End')
    
    ax1.set_xlabel('X (Å)')
    ax1.set_ylabel('Y (Å)')
    ax1.set_zlabel('Z (Å)')
    ax1.set_title(f'3D Trajectory - Atom {atom_id} (Type {atom_type})')
    ax1.legend()
    
    # X coordinate vs time
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(times, coords[:, 0], 'b-', linewidth=2, alpha=0.8)
    ax2.set_xlabel('Time (ps)')
    ax2.set_ylabel('X Coordinate (Å)')
    ax2.set_title('X Position vs Time')
    ax2.grid(True, alpha=0.3)
    
    # Y coordinate vs time  
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.plot(times, coords[:, 1], 'g-', linewidth=2, alpha=0.8)
    ax3.set_xlabel('Time (ps)')
    ax3.set_ylabel('Y Coordinate (Å)')
    ax3.set_title('Y Position vs Time')
    ax3.grid(True, alpha=0.3)
    
    # Z coordinate vs time
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.plot(times, coords[:, 2], 'r-', linewidth=2, alpha=0.8)
    ax4.set_xlabel('Time (ps)')
    ax4.set_ylabel('Z Coordinate (Å)')
    ax4.set_title('Z Position vs Time')
    ax4.grid(True, alpha=0.3)
    
    # XY projection
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.plot(coords[:, 0], coords[:, 1], 'purple', linewidth=2, alpha=0.6)
    ax5.scatter(coords[0, 0], coords[0, 1], c='green', s=80, marker='o', label='Start')
    ax5.scatter(coords[-1, 0], coords[-1, 1], c='red', s=80, marker='s', label='End')
    ax5.set_xlabel('X (Å)')
    ax5.set_ylabel('Y (Å)')
    ax5.set_title('XY Projection')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    ax5.set_aspect('equal', adjustable='box')
    
    # Distance from starting position vs time
    ax6 = fig.add_subplot(2, 3, 6)
    start_pos = coords[0]
    distances = np.linalg.norm(coords - start_pos, axis=1)
    ax6.plot(times, distances, 'orange', linewidth=2, alpha=0.8)
    ax6.set_xlabel('Time (ps)')
    ax6.set_ylabel('Distance from Start (Å)')
    ax6.set_title('Displacement from Initial Position')
    ax6.grid(True, alpha=0.3)
    
    # Add overall title and metadata
    fig.suptitle(f'Atom {atom_id} Trajectory Analysis\n'
                f'Atom Type: {atom_type} | Duration: {times[-1]:.1f} ps | '
                f'Points: {len(coords)}', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    print(f"Trajectory plot saved to: {output_file}")
    
    # Calculate and print some trajectory statistics
    print(f"\nTrajectory Statistics for Atom {atom_id}:")
    print(f"- Atom Type: {atom_type}")
    print(f"- Duration: {times[-1]:.2f} ps")
    print(f"- Total displacement: {distances[-1]:.3f} Å")
    print(f"- Maximum displacement: {np.max(distances):.3f} Å")
    print(f"- Average X: {np.mean(coords[:, 0]):.3f} Å")
    print(f"- Average Y: {np.mean(coords[:, 1]):.3f} Å")  
    print(f"- Average Z: {np.mean(coords[:, 2]):.3f} Å")
    print(f"- X range: [{np.min(coords[:, 0]):.3f}, {np.max(coords[:, 0]):.3f}] Å")
    print(f"- Y range: [{np.min(coords[:, 1]):.3f}, {np.max(coords[:, 1]):.3f}] Å")
    print(f"- Z range: [{np.min(coords[:, 2]):.3f}, {np.max(coords[:, 2]):.3f}] Å")
    
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Plot atom trajectory from LAMMPS ADIOS2 data')
    parser.add_argument('atom_id', type=int, help='Atom ID to track (1-indexed)')
    parser.add_argument('--input', '-i', 
                       default='/mnt/common/jcernudagarcia/demo/phase3/data/nanoparticles.bp5',
                       help='Path to ADIOS2 BP5 file')
    parser.add_argument('--output', '-o', 
                       help='Output PNG file (default: atom_{atom_id}_trajectory.png)')
    
    args = parser.parse_args()
    
    if args.output is None:
        args.output = f'atom_{args.atom_id}_trajectory.png'
    
    print(f"Plotting trajectory for atom {args.atom_id}")
    print(f"Input file: {args.input}")
    print(f"Output file: {args.output}")
    
    # Extract trajectory data
    trajectory_data = get_atom_trajectory(args.input, args.atom_id)
    
    # Create the plot
    plot_atom_trajectory(trajectory_data, args.output)

if __name__ == "__main__":
    main()