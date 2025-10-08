#!/usr/bin/env python3
"""
Comprehensive EarthScope Seismograph Visualization
Creates a publication-quality multi-axis plot of seismic data with metadata
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import json
from datetime import datetime, timedelta

def load_metadata():
    """Load and parse metadata from GeoJSON file"""
    try:
        with open('odsa_metadata.geojson', 'r') as f:
            metadata = json.load(f)
        
        # Extract station information
        station_info = metadata['features'][0]['properties']
        coordinates = metadata['features'][0]['geometry']['coordinates']
        
        return {
            'station_code': station_info.get('station_code', 'ODSA'),
            'network_code': station_info.get('network_code', 'PW'),
            'location_code': station_info.get('location_code', 'LY_'),
            'channel_code': station_info.get('channel_code', '00'),
            'latitude': float(station_info.get('latitude', coordinates[1])),
            'longitude': float(station_info.get('longitude', coordinates[0]))
        }
    except Exception as e:
        print(f"Warning: Could not load metadata - {e}")
        return {
            'station_code': 'ODSA',
            'network_code': 'PW',
            'location_code': 'LY_',
            'channel_code': '00',
            'latitude': 47.329,
            'longitude': -118.713
        }

def create_comprehensive_plot():
    """Create comprehensive seismograph visualization"""
    
    # Load data
    print("Loading seismograph data...")
    df = pd.read_csv('odsa_processed.csv')
    
    # Convert datetime column to proper datetime if it's not already
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Load metadata
    metadata = load_metadata()
    
    # Create figure with subplots
    fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    fig.suptitle(f'EarthScope Seismograph Data - Station {metadata["station_code"]}.{metadata["network_code"]}.{metadata["location_code"]}.{metadata["channel_code"]}\n'
                 f'Location: {metadata["latitude"]:.3f}°N, {abs(metadata["longitude"]):.3f}°W', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Color scheme for each axis
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Blue, Orange, Green
    
    # Plot each component
    components = [
        ('east', 'East Component (m)', 'Eastward displacement'),
        ('north', 'North Component (m)', 'Northward displacement'), 
        ('up', 'Up Component (m)', 'Vertical displacement')
    ]
    
    for i, (component, ylabel, description) in enumerate(components):
        ax = axes[i]
        
        # Subsample data for plotting (every 100th point for performance)
        step = max(1, len(df) // 10000)  # Show max 10k points
        plot_data = df.iloc[::step]
        
        # Create the line plot
        ax.plot(plot_data['datetime'], plot_data[component], 
               color=colors[i], linewidth=0.8, alpha=0.8, label=description)
        
        # Formatting
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right', fontsize=10)
        
        # Add statistics text box
        mean_val = df[component].mean()
        std_val = df[component].std()
        min_val = df[component].min()
        max_val = df[component].max()
        
        stats_text = f'μ={mean_val:.4f}m\nσ={std_val:.4f}m\nRange: [{min_val:.4f}, {max_val:.4f}]m'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8),
               verticalalignment='top', fontsize=9, fontfamily='monospace')
        
        # Highlight significant movements (beyond 2 standard deviations)
        threshold = mean_val + 2 * std_val
        significant = plot_data[abs(plot_data[component] - mean_val) > 2 * std_val]
        if len(significant) > 0:
            ax.scatter(significant['datetime'], significant[component], 
                      color='red', s=1, alpha=0.6, label='Significant events (>2σ)')
    
    # Format x-axis
    axes[-1].set_xlabel('Time', fontsize=12, fontweight='bold')
    
    # Format datetime on x-axis
    duration_hours = (df['datetime'].max() - df['datetime'].min()).total_seconds() / 3600
    
    if duration_hours < 24:
        # For less than 24 hours, show hours:minutes
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        axes[-1].xaxis.set_major_locator(mdates.HourLocator(interval=max(1, int(duration_hours/10))))
        axes[-1].xaxis.set_minor_locator(mdates.MinuteLocator(interval=30))
    elif duration_hours < 7*24:
        # For less than a week, show day-month hour
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=1))
        axes[-1].xaxis.set_minor_locator(mdates.HourLocator(interval=6))
    else:
        # For longer periods, show day-month
        axes[-1].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        axes[-1].xaxis.set_major_locator(mdates.DayLocator(interval=max(1, int(duration_hours/(24*10)))))
        axes[-1].xaxis.set_minor_locator(mdates.HourLocator(interval=12))
    
    # Rotate x-axis labels for better readability
    plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add data information footer
    data_info = (f'Data Period: {df["datetime"].min().strftime("%Y-%m-%d %H:%M:%S")} to {df["datetime"].max().strftime("%Y-%m-%d %H:%M:%S")} UTC\n'
                f'Duration: {duration_hours:.1f} hours | Sample Rate: 1 Hz | Total Points: {len(df):,}\n'
                f'Data Source: EarthScope Consortium via National Data Platform')
    
    fig.text(0.02, 0.02, data_info, fontsize=9, fontfamily='monospace', 
             bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.subplots_adjust(top=0.9, bottom=0.15)
    
    # Save the plot
    output_file = 'earthscope_seismograph_comprehensive.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    print(f"Comprehensive visualization saved as: {output_file}")
    
    # Also save as high-quality PDF
    pdf_file = 'earthscope_seismograph_comprehensive.pdf'
    plt.savefig(pdf_file, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    print(f"PDF version saved as: {pdf_file}")
    
    plt.show()

if __name__ == "__main__":
    create_comprehensive_plot()