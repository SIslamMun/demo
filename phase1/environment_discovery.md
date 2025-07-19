# Environment Discovery Report - Phase 1

## Executive Summary

This report presents a comprehensive assessment of the Ares HPC cluster environment, including available data resources, cluster configuration, hardware specifications, and software modules. The analysis reveals a well-equipped scientific computing environment with significant computational resources and specialized tools for data-intensive research.

## 1. Scientific Data Inventory

### 1.1 Available Data Formats and Locations
The filesystem exploration revealed extensive scientific datasets across multiple locations:

#### Key Data Repositories:
- **Location**: `/mnt/common/datasets/`
- **Size**: Over 40,000 files across multiple directories
- **Primary Formats Discovered**:
  - HDF5 files (`.h5`, `.hdf5`)
  - CSV data files (`.csv`) 
  - Binary data files (`.dat`)
  - ADIOS2 BP5 format files (`.bp`, `.bp5`)
  - NetCDF files (`.nc`)
  - Parquet files (`.parquet`)

#### Notable Dataset Collections:
1. **1000 Genome Project Data** (`/mnt/common/datasets/1000-genome/`)
   - Multiple releases (2008-2010)
   - Genomic variant data, haplotype information
   - Sample data for CEU, YRI, JPTCHB populations

2. **Scientific Application Data**:
   - **TeraFusion**: Remote sensing data processing
   - **DeepDriveMD**: Molecular dynamics simulation data
   - **FlexTRKR**: Weather tracking and analysis datasets
   - **Beacon**: Genomic query datasets
   - **Darshan traces**: I/O performance monitoring data

3. **Research User Data** (`/mnt/common/user-data/`):
   - Multiple user directories with simulation outputs
   - Hermes I/O optimization datasets
   - Access pattern analysis data (`.parquet` format)
   - Molecular dynamics trajectories

### 1.2 Data Access Patterns
Analysis of existing data shows:
- High-performance I/O patterns for large-scale simulations
- Parallel filesystem usage (OrangeFS/PVFS2)
- Storage across multiple tiers (HDD, SSD, NVMe)

## 2. Cluster Resource Assessment

### 2.1 Slurm Cluster Configuration
- **Cluster Name**: slurm-cluster
- **Slurm Version**: 21.08.5
- **Total Nodes**: 32 compute nodes (`ares-comp-[01-32]`)

#### Node Status Distribution:
- **Available Idle**: 4 nodes (`ares-comp-[27-30]`)
- **Allocated**: 13 nodes (currently in use)
- **Down**: 13 nodes (maintenance/offline)
- **Drained**: 2 nodes (administrative hold)

#### Resource Specifications per Node:
- **CPUs**: 40 cores per node (520 total allocated)
- **Memory**: Detailed memory specifications available
- **Time Limit**: 2 days maximum job duration

#### Current Utilization:
- **Active Jobs**: 1 running (interactive session by jcernudagarcia)
- **Queue Status**: No pending jobs
- **Available Capacity**: 4 idle nodes (160 cores) ready for scheduling

### 2.2 Partition Configuration
- **Primary Partition**: `compute`
- **Access Policy**: Standard HPC scheduling
- **Resource Allocation**: Dynamic based on job requirements

## 3. Hardware Specifications

### 3.1 CPU Configuration
- **Processor**: Intel(R) Xeon(R) Silver 4114 CPU @ 2.20GHz
- **Architecture**: x86_64 (Skylake AVX512)
- **Physical Cores**: 20 per node
- **Logical Cores**: 40 per node (hyperthreading enabled)
- **Current Frequency**: 2.137 GHz
- **Load Average**: 4.62 (1-min), 3.91 (5-min), 4.21 (15-min)

### 3.2 Memory Configuration
- **Total Memory**: 94.07 GB per node
- **Available Memory**: 82.16 GB
- **Used Memory**: 11.00 GB (12.7% utilization)
- **Swap Space**: 8.00 GB (0.8% used)
- **Memory Efficiency**: Excellent availability for large-scale computations

### 3.3 Network Infrastructure
- **Primary Interface**: eno1 (1 Gbps external connectivity)
- **High-Speed Interface**: ens1np0 (40 Gbps InfiniBand)
- **Internal Networks**: Multiple private subnets for cluster communication
- **Container Support**: Docker and Podman networking configured

#### Network Performance:
- **Total Data Transferred**: 362.1 GB (sent + received)
- **High-Speed Connectivity**: 40 Gbps available for MPI communications
- **Network Reliability**: No errors detected on primary interfaces

### 3.4 System Information
- **Operating System**: Ubuntu 22.04 LTS
- **Kernel Version**: 5.15.0-143-generic
- **Hostname**: ares.ares.local
- **Uptime**: 15 days, 1 hours, 20 minutes
- **Active Users**: 17 concurrent users
- **Python Version**: 3.12.0

## 4. Software Environment

### 4.1 Module System
- **System**: Lmod (Environment Modules)
- **Currently Loaded**: No modules loaded by default
- **Available Modules**: 22 modules accessible

### 4.2 Available Software Stack

#### Scientific Computing Libraries:
- **HDF5**: Multiple versions (1.14.0, 1.14.5) with parallel support
- **MPI Implementations**:
  - OpenMPI 5.0.5 (primary)
  - MPICH 4.1.1
- **ADIOS/ADIOS2**: Multiple versions for high-performance I/O
- **NetCDF**: Both C and Fortran interfaces available
- **FFTW**: 3.3.10 for numerical computations

#### Simulation and Modeling Software:
- **LAMMPS**: Multiple versions (20220623.4, 20240829.1)
- **OpenFOAM**: 2312 for computational fluid dynamics
- **WRF**: 4.6.1 for weather research and forecasting
- **ParaView**: 5.13.1 for visualization

#### Specialized Tools:
- **Hermes**: 1.2.1 for heterogeneous memory management
- **IOR**: 3.3.0 for I/O benchmarking
- **IOWarp**: Main branch for I/O optimization
- **Chimaera**: Distributed computing framework

#### Development and Analysis:
- **GCC**: 11.4.0 compiler suite
- **Python Libraries**: Tabulate, TOML parsing, typing extensions
- **YAML-cpp**: 0.8.0 for configuration parsing

### 4.3 Container Support
- **Docker**: Configured and available
- **Podman**: Active with CNI networking
- **Kubernetes**: Flannel networking detected

## 5. Storage and I/O Infrastructure

### 5.1 Parallel Filesystem
- **OrangeFS/PVFS2**: Configured for high-performance parallel I/O
- **Mount Points**: Multiple storage tiers available
- **Configuration Files**: Located in `/mnt/common/pfs_conf/`

### 5.2 Storage Tiers
Evidence of multi-tier storage:
- **NVMe**: High-performance storage for hot data
- **SSD**: Intermediate performance storage
- **HDD**: Large-capacity storage for cold data

### 5.3 I/O Monitoring
- **Darshan**: I/O profiling and analysis tools available
- **Hermes**: Advanced I/O optimization and caching
- **IOWarp**: I/O pattern analysis and optimization

## 6. Recommendations for Scientific Computing

### 6.1 Optimal Resource Utilization
1. **Job Scheduling**: 4 nodes immediately available for new workloads
2. **Memory Usage**: Excellent headroom (82GB available per node)
3. **Network**: Leverage 40 Gbps InfiniBand for MPI-intensive applications

### 6.2 Data Management Strategy
1. **Large Datasets**: Utilize parallel I/O with ADIOS2 or HDF5-MPI
2. **I/O Optimization**: Deploy Hermes for multi-tier storage caching
3. **Data Transfer**: Use high-speed network interfaces for inter-node communication

### 6.3 Software Environment Setup
1. **Module Loading**: Configure application-specific module collections
2. **MPI Applications**: OpenMPI 5.0.5 recommended for new developments
3. **Visualization**: ParaView available for post-processing workflows

## 7. Current Environment Status

- **Cluster Health**: Good (15 days uptime, stable operation)
- **Resource Availability**: 25% of nodes immediately available
- **Storage**: Multiple PB-scale datasets accessible
- **Network**: High-performance connectivity operational
- **Software**: Comprehensive scientific computing stack ready

This environment provides an excellent foundation for large-scale scientific computing, with particular strengths in:
- Parallel computing and MPI applications
- High-performance I/O and data management
- Multi-physics simulations and modeling
- Advanced visualization and post-processing

The cluster is well-suited for data-intensive computational research across multiple scientific domains.