#!/usr/bin/env python3
"""
Analyze LAMMPS GO-Nanoparticle Dataset from ADIOS2 BP5 format
"""

import numpy as np
from adios2 import FileReader
import json
import os

def analyze_nanoparticles_dataset(bp_file_path):
    """Analyze the nanoparticles.bp5 dataset and generate a comprehensive report"""
    
    results = {
        "dataset_info": {},
        "variables": {},
        "simulation_parameters": {},
        "analysis": {}
    }
    
    print(f"Analyzing ADIOS2 dataset: {bp_file_path}")
    
    try:
        with FileReader(bp_file_path) as reader:
            # Get available variables
            variables = reader.available_variables()
            print(f"Found {len(variables)} variables in the dataset")
            
            results["dataset_info"]["total_variables"] = len(variables)
            results["dataset_info"]["file_path"] = bp_file_path
            
            # Analyze each variable
            for var_name, var_info in variables.items():
                print(f"\nVariable: {var_name}")
                for key, value in var_info.items():
                    print(f"  {key}: {value}")
                
                results["variables"][var_name] = var_info
                
                # Read key variables for analysis
                if var_name == "ntimestep":
                    # Get total number of steps
                    steps_count = int(var_info.get('AvailableStepsCount', 1))
                    timesteps = reader.read(var_name, step_selection=[0, steps_count])
                    results["simulation_parameters"]["total_steps"] = steps_count
                    results["simulation_parameters"]["timestep_range"] = [int(timesteps.min()), int(timesteps.max())]
                    
                elif var_name == "natoms":
                    natoms = reader.read(var_name)
                    results["simulation_parameters"]["total_atoms"] = int(natoms[0]) if natoms.ndim > 0 else int(natoms)
                    
                elif var_name in ["boxxlo", "boxxhi", "boxylo", "boxyhi", "boxzlo", "boxzhi"]:
                    box_val = reader.read(var_name)
                    results["simulation_parameters"][var_name] = float(box_val[0]) if box_val.ndim > 0 else float(box_val)
                
                elif var_name == "ncolumns":
                    ncolumns = reader.read(var_name)
                    results["simulation_parameters"]["atom_data_columns"] = int(ncolumns[0]) if ncolumns.ndim > 0 else int(ncolumns)
            
            # Calculate simulation box dimensions
            if all(key in results["simulation_parameters"] for key in ["boxxlo", "boxxhi", "boxylo", "boxyhi", "boxzlo", "boxzhi"]):
                box_x = results["simulation_parameters"]["boxxhi"] - results["simulation_parameters"]["boxxlo"]
                box_y = results["simulation_parameters"]["boxyhi"] - results["simulation_parameters"]["boxylo"]  
                box_z = results["simulation_parameters"]["boxzhi"] - results["simulation_parameters"]["boxzlo"]
                
                results["simulation_parameters"]["box_dimensions"] = {
                    "x": box_x,
                    "y": box_y, 
                    "z": box_z,
                    "volume": box_x * box_y * box_z
                }
            
            # Analyze atom data structure (first few steps only due to size)
            if "atoms" in variables:
                atoms_info = variables["atoms"]
                results["analysis"]["atoms_analysis"] = {
                    "shape": atoms_info.get("Shape", "Unknown"),
                    "type": atoms_info.get("Type", "Unknown"),
                    "available_steps": atoms_info.get("AvailableStepsCount", "Unknown"),
                    "note": "Atom data contains: [ID, type, x_scaled, y_scaled, z_scaled]"
                }
                
                # Sample analysis for first step
                try:
                    # Read atoms data for step 0 only (to avoid memory issues)
                    atoms_step0 = reader.read("atoms", step_selection=[0, 1])
                    if atoms_step0 is not None and atoms_step0.size > 0:
                        results["analysis"]["sample_atoms_step0"] = {
                            "shape": list(atoms_step0.shape),
                            "atom_types_present": list(np.unique(atoms_step0[:, 1]).astype(int)),
                            "coordinate_ranges": {
                                "x_scaled": [float(atoms_step0[:, 2].min()), float(atoms_step0[:, 2].max())],
                                "y_scaled": [float(atoms_step0[:, 3].min()), float(atoms_step0[:, 3].max())],
                                "z_scaled": [float(atoms_step0[:, 4].min()), float(atoms_step0[:, 4].max())]
                            }
                        }
                except Exception as e:
                    results["analysis"]["atoms_read_error"] = f"Could not read atoms data: {str(e)}"
            
            # Calculate simulation time information
            if "ntimestep" in results["simulation_parameters"]:
                timestep_fs = 1.0  # 1.0 fs per timestep as per metadata
                max_step = results["simulation_parameters"]["timestep_range"][1]
                total_time_ps = max_step * timestep_fs / 1000.0  # Convert fs to ps
                
                results["analysis"]["temporal_info"] = {
                    "timestep_size_fs": timestep_fs,
                    "total_simulation_time_ps": total_time_ps,
                    "output_frequency": "Every 1000 steps (1 ps)",
                    "total_output_steps": results["simulation_parameters"]["total_steps"]
                }
    
    except Exception as e:
        results["error"] = f"Error analyzing dataset: {str(e)}"
        print(f"Error: {e}")
    
    return results

def generate_report(analysis_results):
    """Generate a formatted report from analysis results"""
    
    report = []
    report.append("# LAMMPS GO-Nanoparticle Dataset Analysis Report")
    report.append("=" * 50)
    
    # Dataset Information
    if "dataset_info" in analysis_results:
        report.append("\n## Dataset Information")
        info = analysis_results["dataset_info"]
        report.append(f"- File: {info.get('file_path', 'Unknown')}")
        report.append(f"- Total Variables: {info.get('total_variables', 'Unknown')}")
    
    # Simulation Parameters
    if "simulation_parameters" in analysis_results:
        report.append("\n## Simulation Parameters")
        params = analysis_results["simulation_parameters"]
        
        if "total_atoms" in params:
            report.append(f"- Total Atoms: {params['total_atoms']}")
        if "total_steps" in params:
            report.append(f"- Total Output Steps: {params['total_steps']}")
        if "timestep_range" in params:
            report.append(f"- Timestep Range: {params['timestep_range'][0]} - {params['timestep_range'][1]}")
        if "atom_data_columns" in params:
            report.append(f"- Atom Data Columns: {params['atom_data_columns']}")
        
        if "box_dimensions" in params:
            box = params["box_dimensions"]
            report.append(f"- Simulation Box: {box['x']:.1f} × {box['y']:.1f} × {box['z']:.1f} Å³")
            report.append(f"- Box Volume: {box['volume']:.1f} Å³")
    
    # Analysis Results
    if "analysis" in analysis_results:
        report.append("\n## Analysis Results")
        analysis = analysis_results["analysis"]
        
        if "temporal_info" in analysis:
            temp = analysis["temporal_info"]
            report.append(f"- Timestep Size: {temp['timestep_size_fs']} fs")
            report.append(f"- Total Simulation Time: {temp['total_simulation_time_ps']} ps")
            report.append(f"- Output Frequency: {temp['output_frequency']}")
        
        if "atoms_analysis" in analysis:
            atoms = analysis["atoms_analysis"]
            report.append(f"- Atoms Data Shape: {atoms['shape']}")
            report.append(f"- Atoms Data Type: {atoms['type']}")
            report.append(f"- Available Steps: {atoms['available_steps']}")
            report.append(f"- Note: {atoms['note']}")
        
        if "sample_atoms_step0" in analysis:
            sample = analysis["sample_atoms_step0"]
            report.append(f"- Atom Types Present (Step 0): {sample['atom_types_present']}")
            coord_ranges = sample['coordinate_ranges']
            report.append(f"- X Coordinate Range (scaled): {coord_ranges['x_scaled'][0]:.3f} - {coord_ranges['x_scaled'][1]:.3f}")
            report.append(f"- Y Coordinate Range (scaled): {coord_ranges['y_scaled'][0]:.3f} - {coord_ranges['y_scaled'][1]:.3f}")
            report.append(f"- Z Coordinate Range (scaled): {coord_ranges['z_scaled'][0]:.3f} - {coord_ranges['z_scaled'][1]:.3f}")
    
    # Variables Information
    if "variables" in analysis_results:
        report.append("\n## Variables in Dataset")
        for var_name, var_info in analysis_results["variables"].items():
            report.append(f"- **{var_name}**: {var_info.get('Type', 'Unknown type')}")
            if 'Shape' in var_info and var_info['Shape']:
                report.append(f"  - Shape: {var_info['Shape']}")
            if 'AvailableStepsCount' in var_info:
                report.append(f"  - Steps: {var_info['AvailableStepsCount']}")
    
    if "error" in analysis_results:
        report.append(f"\n## Error\n{analysis_results['error']}")
    
    return "\n".join(report)

def main():
    # Analyze the nanoparticles dataset
    bp_file = "/mnt/common/jcernudagarcia/demo/phase3/data/nanoparticles.bp5"
    
    print("Starting nanoparticles dataset analysis...")
    results = analyze_nanoparticles_dataset(bp_file)
    
    # Generate report
    report = generate_report(results)
    print("\n" + "="*60)
    print("ANALYSIS REPORT")
    print("="*60)
    print(report)
    
    # Save detailed results as JSON
    with open("/mnt/common/jcernudagarcia/demo/phase3/nanoparticles_analysis.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed analysis saved to: nanoparticles_analysis.json")
    
    return results, report

if __name__ == "__main__":
    main()