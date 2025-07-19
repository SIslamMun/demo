#!/usr/bin/env python3
"""
Plot the trajectory of a single atom over time from LAMMPS ADIOS2 BP5 output.

This script reads the nanoparticles.bp5 file and plots the 3D trajectory
of a specified atom over all simulation timesteps.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import adios2


def convert_scaled_to_real(scaled_coords, box_lo, box_hi):
    """Convert scaled coordinates (0-1) to real coordinates."""
    return scaled_coords * (box_hi - box_lo) + box_lo


def plot_atom_trajectory(bp5_file, atom_id, output_file=None):
    """
    Plot the trajectory of a single atom over time.
    
    Parameters:
    -----------
    bp5_file : str
        Path to the ADIOS2 BP5 file
    atom_id : int
        ID of the atom to track
    output_file : str, optional
        Output PNG file name. If None, uses atom_{atom_id}_trajectory.png
    """
    
    if output_file is None:
        output_file = f"atom_{atom_id}_trajectory.png"
    
    # Lists to store trajectory data
    x_coords = []
    y_coords = []
    z_coords = []
    timesteps = []
    
    print(f"Reading trajectory data for atom ID {atom_id}...")
    
    try:
        # Read the BP5 file using ADIOS2
        with adios2.Stream(bp5_file, "r") as stream:
            step_count = 0
            
            for _ in stream.steps():
                # Read current timestep
                ntimestep = stream.read("ntimestep")
                
                # Read atom data
                atoms = stream.read("atoms")
                
                # Read box dimensions
                boxxlo = stream.read("boxxlo")
                boxxhi = stream.read("boxxhi")
                boxylo = stream.read("boxylo")
                boxyhi = stream.read("boxyhi")
                boxzlo = stream.read("boxzlo")
                boxzhi = stream.read("boxzhi")
                
                # Find the atom with the specified ID
                # atoms array columns: [id, type, xs, ys, zs]
                atom_indices = np.where(atoms[:, 0] == atom_id)[0]
                
                if len(atom_indices) == 0:
                    print(f"Warning: Atom ID {atom_id} not found at timestep {ntimestep}")
                    continue
                
                # Get the atom data (should be unique)
                atom_data = atoms[atom_indices[0]]
                
                # Extract scaled coordinates
                xs, ys, zs = atom_data[2], atom_data[3], atom_data[4]
                
                # Convert to real coordinates
                x_real = convert_scaled_to_real(xs, boxxlo, boxxhi)
                y_real = convert_scaled_to_real(ys, boxylo, boxyhi)
                z_real = convert_scaled_to_real(zs, boxzlo, boxzhi)
                
                # Store data
                x_coords.append(x_real)
                y_coords.append(y_real)
                z_coords.append(z_real)
                timesteps.append(ntimestep)
                
                step_count += 1
                if step_count % 10 == 0:
                    print(f"Processed {step_count} steps...")
    
    except Exception as e:
        print(f"Error reading ADIOS2 file: {e}")
        return
    
    if len(x_coords) == 0:
        print(f"No data found for atom ID {atom_id}")
        return
    
    # Convert to numpy arrays
    x_coords = np.array(x_coords)
    y_coords = np.array(y_coords)
    z_coords = np.array(z_coords)
    timesteps = np.array(timesteps)
    
    print(f"Found {len(timesteps)} timesteps for atom {atom_id}")
    
    # Create the 3D trajectory plot
    fig = plt.figure(figsize=(12, 10))
    
    # 3D trajectory plot
    ax1 = fig.add_subplot(221, projection='3d')
    scatter = ax1.scatter(x_coords, y_coords, z_coords, c=timesteps, 
                         cmap='viridis', s=30, alpha=0.7)
    ax1.plot(x_coords, y_coords, z_coords, 'k-', alpha=0.3, linewidth=0.5)
    ax1.set_xlabel('X (Å)')
    ax1.set_ylabel('Y (Å)')
    ax1.set_zlabel('Z (Å)')
    ax1.set_title(f'3D Trajectory - Atom {atom_id}')
    plt.colorbar(scatter, ax=ax1, label='Timestep', shrink=0.8)
    
    # X-Y projection
    ax2 = fig.add_subplot(222)
    ax2.scatter(x_coords, y_coords, c=timesteps, cmap='viridis', s=20, alpha=0.7)
    ax2.plot(x_coords, y_coords, 'k-', alpha=0.3, linewidth=0.5)
    ax2.set_xlabel('X (Å)')
    ax2.set_ylabel('Y (Å)')
    ax2.set_title('X-Y Projection')
    ax2.grid(True, alpha=0.3)
    
    # Time series plots
    time_ps = timesteps * 1e-3  # Convert to picoseconds
    
    ax3 = fig.add_subplot(223)
    ax3.plot(time_ps, x_coords, 'r-', label='X', linewidth=1)
    ax3.plot(time_ps, y_coords, 'g-', label='Y', linewidth=1)
    ax3.plot(time_ps, z_coords, 'b-', label='Z', linewidth=1)
    ax3.set_xlabel('Time (ps)')
    ax3.set_ylabel('Position (Å)')
    ax3.set_title('Position vs Time')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Distance from origin
    distances = np.sqrt(x_coords**2 + y_coords**2 + z_coords**2)
    ax4 = fig.add_subplot(224)
    ax4.plot(time_ps, distances, 'purple', linewidth=1.5)
    ax4.set_xlabel('Time (ps)')
    ax4.set_ylabel('Distance from Origin (Å)')
    ax4.set_title('Distance from Origin vs Time')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Trajectory plot saved as: {output_file}")
    
    # Print some statistics
    print(f"\nTrajectory Statistics for Atom {atom_id}:")
    print(f"Time range: {time_ps[0]:.3f} - {time_ps[-1]:.3f} ps")
    print(f"X range: {x_coords.min():.3f} - {x_coords.max():.3f} Å")
    print(f"Y range: {y_coords.min():.3f} - {y_coords.max():.3f} Å")
    print(f"Z range: {z_coords.min():.3f} - {z_coords.max():.3f} Å")
    print(f"Distance range: {distances.min():.3f} - {distances.max():.3f} Å")
    print(f"Average distance from origin: {distances.mean():.3f} ± {distances.std():.3f} Å")


def main():
    parser = argparse.ArgumentParser(description='Plot atom trajectory from LAMMPS ADIOS2 output')
    parser.add_argument('atom_id', type=int, help='ID of the atom to track')
    parser.add_argument('--input', '-i', default='data/nanoparticles.bp5',
                        help='Input BP5 file path (default: data/nanoparticles.bp5)')
    parser.add_argument('--output', '-o', help='Output PNG file name')
    
    args = parser.parse_args()
    
    plot_atom_trajectory(args.input, args.atom_id, args.output)


if __name__ == "__main__":
    main()