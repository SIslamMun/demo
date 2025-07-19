# Data Inventory Report
*Generated on: July 19, 2025*

## Executive Summary

This report provides a comprehensive analysis of two distinct datasets used in Phase 3 of the multi-format data processing project:
1. **Nanoparticles Dataset** - ADIOS BP5 format containing molecular dynamics simulation data
2. **Sensor Data Dataset** - CSV format containing temperature sensor measurements

## Dataset 1: Nanoparticles (ADIOS BP5 Format)

### Overview
- **File Path**: `data/nanoparticles.bp5`
- **Format**: ADIOS BP5 (Binary Pack format)
- **Source**: LAMMPS molecular dynamics simulation
- **Domain**: Material science - graphene oxide nanoparticle interactions with water

### Simulation Context
- **System**: Graphene oxide nanoparticle in vacuum with 3 water molecules
- **Temperature**: 300 K (room temperature)
- **Duration**: 50 picoseconds (50,000 timesteps)
- **Timestep**: 1.0 fs
- **Total Atoms**: 272 atoms across 15 atom types
- **Box Dimensions**: 54.4 × 54.4 × 54.4 Å³ cubic cell

### Data Structure
- **Available Steps**: 51 timesteps (0 to 50,000, saved every 1000 steps)
- **Primary Variables**:
  - `atoms`: 2D array (272 × 5) containing atom ID, type, and scaled coordinates (xs, ys, zs)
  - `ntimestep`: Simulation timestep ranging from 0 to 50,000
  - `natoms`: Constant value of 272 atoms
  - `ncolumns`: 5 columns in atoms array
  - Box boundaries: `boxxlo`, `boxxhi`, `boxylo`, `boxyhi`, `boxzlo`, `boxzhi` (-27.2 to 27.2 Å)

### Key Attributes
- **LAMMPS Version**: 29 Aug 2024 (20240829)
- **Dump Style**: atom
- **Boundary Conditions**: Periodic in all directions ("pp pp pp")
- **Coordinate System**: Scaled coordinates (0-1 range)
- **Columns**: ["id", "type", "xs", "ys", "zs"]

### Data Characteristics
- **Data Range**: 
  - Atoms variable: Min = 0.257623, Max = 7169
  - Box dimensions: Fixed at ±27.2 Å in all directions
- **Single Processor Output**: nprocs = 1, offset = 0
- **Complete Dataset**: No missing timesteps, consistent atom count

### Scientific Applications
This dataset enables analysis of:
- Graphene oxide-water molecular interactions
- Water molecule diffusion and mobility patterns
- Hydrogen bonding networks
- Structural stability analysis
- Radial distribution functions

## Dataset 2: Sensor Data (CSV Format)

### Overview
- **File Path**: `data/sensor_data.csv`
- **Format**: CSV (Comma-Separated Values)
- **Domain**: Environmental monitoring - temperature sensor measurements
- **Data Type**: Time series temperature data

### Data Structure
- **Rows**: 50 measurements
- **Columns**: 2 (timestamp, sensor_value)
- **Memory Usage**: 3.9 KB
- **Time Range**: January 1, 2024, 00:00:00 to 04:05:00
- **Sampling Interval**: 5 minutes

### Statistical Analysis
#### Temperature Measurements (sensor_value):
- **Count**: 50 observations
- **Mean**: 24.97°C
- **Standard Deviation**: 0.92°C
- **Range**: 23.45°C to 26.89°C
- **Median**: 24.93°C
- **Interquartile Range**: 1.44°C

#### Distribution Characteristics:
- **Skewness**: 0.14 (slightly right-skewed)
- **Kurtosis**: -0.93 (platykurtic - flatter than normal distribution)
- **Coefficient of Variation**: 3.69% (low variability)

#### Data Quality:
- **Missing Values**: 0 (100% complete)
- **Unique Timestamps**: 50 (no duplicates)
- **Temperature Stability**: Values cluster around 25°C with minimal variation

### Temporal Characteristics
- **Duration**: 4 hours and 5 minutes
- **Regular Sampling**: Consistent 5-minute intervals
- **Seasonal Pattern**: Not applicable (short duration)
- **Trend**: Stable temperature with minor fluctuations

## Comparative Analysis

### Data Format Comparison
| Aspect | Nanoparticles (BP5) | Sensor Data (CSV) |
|--------|-------------------|------------------|
| **Complexity** | High (multidimensional molecular data) | Low (simple time series) |
| **File Size** | Large (molecular trajectory) | Small (50 measurements) |
| **Temporal Resolution** | 1000 timesteps (1 ps intervals) | 5-minute intervals |
| **Data Dimensions** | 3D spatial + temporal | 1D temporal |
| **Domain** | Computational physics/chemistry | Environmental monitoring |

### Processing Requirements
- **Nanoparticles**: Requires specialized ADIOS tools, coordinate transformation, large memory for full analysis
- **Sensor Data**: Standard pandas operations, minimal computational requirements

### Scientific Value
- **Nanoparticles**: High scientific value for materials research, nanotechnology applications
- **Sensor Data**: Practical value for environmental monitoring, simple baseline temperature measurements

## Recommendations

### For Nanoparticles Dataset:
1. Use Python ADIOS2 API for large-scale trajectory analysis
2. Convert scaled coordinates to real coordinates using box dimensions
3. Focus analysis on water-graphene oxide interactions
4. Consider memory management for full trajectory processing

### For Sensor Data:
1. Well-suited for time series analysis and trend detection
2. Could benefit from longer-term data collection for pattern identification
3. Ideal for testing data processing pipelines due to simplicity
4. Consider expanding to include additional environmental parameters

## Conclusion

Both datasets represent different scales and domains of scientific data:
- The **nanoparticles dataset** provides rich, complex molecular dynamics data suitable for advanced materials science research
- The **sensor data** offers clean, simple environmental measurements ideal for monitoring applications

The combination demonstrates the versatility required for multi-format scientific data processing workflows, from high-performance computing outputs to standard sensor measurements.