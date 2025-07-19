#!/usr/bin/env python3
"""
Sensor Data CSV Analysis Script
Analyzes temperature sensor data from CSV format
"""

import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

def analyze_sensor_data_csv(file_path):
    """Analyze the sensor_data.csv dataset"""
    
    print("="*60)
    print("Sensor Data Temperature Analysis")
    print("="*60)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    analysis_results = {}
    
    try:
        # Load the CSV data
        print(f"Loading data from: {file_path}")
        df = pd.read_csv(file_path)
        print(f"Successfully loaded CSV with {len(df)} rows and {len(df.columns)} columns")
        print()
        
        # Display basic info about the dataset
        print("Dataset Overview:")
        print("-" * 40)
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print()
        
        print("Column Information:")
        print(df.info())
        print()
        
        print("First few rows:")
        print(df.head())
        print()
        
        print("Last few rows:")
        print(df.tail())
        print()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Basic statistics
        print("Statistical Summary:")
        print("-" * 40)
        print(df.describe())
        print()
        
        analysis_results['basic_stats'] = {
            'shape': df.shape,
            'columns': list(df.columns),
            'temperature_stats': df['sensor_value'].describe().to_dict()
        }
        
        # Time series analysis
        print("Time Series Analysis:")
        print("-" * 40)
        
        # Time range
        start_time = df['timestamp'].min()
        end_time = df['timestamp'].max()
        duration = end_time - start_time
        
        print(f"Time range: {start_time} to {end_time}")
        print(f"Total duration: {duration}")
        
        # Time intervals
        time_diffs = df['timestamp'].diff().dropna()
        avg_interval = time_diffs.mean()
        
        print(f"Average sampling interval: {avg_interval}")
        print(f"Total data points: {len(df)}")
        
        # Check for missing timestamps
        expected_timestamps = pd.date_range(start=start_time, end=end_time, freq=avg_interval)
        missing_timestamps = len(expected_timestamps) - len(df)
        print(f"Missing data points: {missing_timestamps}")
        
        analysis_results['temporal_analysis'] = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_hours': duration.total_seconds() / 3600,
            'sampling_interval_minutes': avg_interval.total_seconds() / 60,
            'total_points': len(df),
            'missing_points': missing_timestamps
        }
        
        # Temperature analysis
        print("\nTemperature Analysis:")
        print("-" * 40)
        
        temp_data = df['sensor_value']
        
        print(f"Temperature range: {temp_data.min():.2f}°C to {temp_data.max():.2f}°C")
        print(f"Mean temperature: {temp_data.mean():.2f}°C")
        print(f"Median temperature: {temp_data.median():.2f}°C")
        print(f"Standard deviation: {temp_data.std():.2f}°C")
        
        # Temperature distribution
        print(f"\nTemperature percentiles:")
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        for p in percentiles:
            print(f"  {p}th percentile: {np.percentile(temp_data, p):.2f}°C")
        
        # Outlier detection (using IQR method)
        Q1 = temp_data.quantile(0.25)
        Q3 = temp_data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = temp_data[(temp_data < lower_bound) | (temp_data > upper_bound)]
        print(f"\nOutlier Analysis (IQR method):")
        print(f"  Lower bound: {lower_bound:.2f}°C")
        print(f"  Upper bound: {upper_bound:.2f}°C")
        print(f"  Number of outliers: {len(outliers)}")
        if len(outliers) > 0:
            print(f"  Outlier values: {outliers.tolist()}")
        
        analysis_results['temperature_analysis'] = {
            'min_temp': float(temp_data.min()),
            'max_temp': float(temp_data.max()),
            'mean_temp': float(temp_data.mean()),
            'median_temp': float(temp_data.median()),
            'std_temp': float(temp_data.std()),
            'percentiles': {str(p): float(np.percentile(temp_data, p)) for p in percentiles},
            'outliers': {
                'count': len(outliers),
                'values': outliers.tolist() if len(outliers) > 0 else [],
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            }
        }
        
        # Trend analysis
        print("\nTrend Analysis:")
        print("-" * 40)
        
        # Calculate moving averages
        df['temp_ma_10'] = temp_data.rolling(window=10, center=True).mean()
        df['temp_ma_60'] = temp_data.rolling(window=60, center=True).mean()
        
        # Calculate rate of change
        df['temp_change'] = temp_data.diff()
        df['temp_change_rate'] = df['temp_change'] / (time_diffs.dt.total_seconds() / 60)  # °C per minute
        
        print(f"Maximum temperature increase rate: {df['temp_change_rate'].max():.4f}°C/min")
        print(f"Maximum temperature decrease rate: {df['temp_change_rate'].min():.4f}°C/min")
        print(f"Average absolute change rate: {df['temp_change_rate'].abs().mean():.4f}°C/min")
        
        # Stability analysis
        temp_stability = df['temp_change'].abs().mean()
        print(f"Temperature stability (avg absolute change): {temp_stability:.3f}°C")
        
        # Count significant changes
        significant_changes = df[df['temp_change'].abs() > 2 * temp_data.std()]
        print(f"Significant temperature changes (> 2σ): {len(significant_changes)}")
        
        analysis_results['trend_analysis'] = {
            'max_increase_rate': float(df['temp_change_rate'].max()),
            'max_decrease_rate': float(df['temp_change_rate'].min()),
            'avg_change_rate': float(df['temp_change_rate'].abs().mean()),
            'temperature_stability': float(temp_stability),
            'significant_changes': len(significant_changes)
        }
        
        # Data quality assessment
        print("\nData Quality Assessment:")
        print("-" * 40)
        
        # Check for missing values
        missing_values = df.isnull().sum()
        print(f"Missing values per column:")
        for col, count in missing_values.items():
            print(f"  {col}: {count}")
        
        # Check for duplicated timestamps
        duplicate_timestamps = df['timestamp'].duplicated().sum()
        print(f"Duplicate timestamps: {duplicate_timestamps}")
        
        # Check for unrealistic temperature values (assuming reasonable range)
        reasonable_range = (-50, 100)  # Reasonable temperature range in Celsius
        unrealistic_temps = df[(df['sensor_value'] < reasonable_range[0]) | 
                              (df['sensor_value'] > reasonable_range[1])]
        print(f"Unrealistic temperature values (outside {reasonable_range}°C): {len(unrealistic_temps)}")
        
        # Data completeness
        data_completeness = (len(df) / len(expected_timestamps)) * 100 if len(expected_timestamps) > 0 else 100
        print(f"Data completeness: {data_completeness:.1f}%")
        
        analysis_results['data_quality'] = {
            'missing_values': missing_values.to_dict(),
            'duplicate_timestamps': duplicate_timestamps,
            'unrealistic_values': len(unrealistic_temps),
            'data_completeness_percent': float(data_completeness)
        }
        
        # Summary insights
        print("\nKey Insights:")
        print("-" * 40)
        print(f"• Dataset spans {duration.total_seconds()/3600:.1f} hours with {len(df)} temperature measurements")
        print(f"• Temperature varies between {temp_data.min():.1f}°C and {temp_data.max():.1f}°C")
        print(f"• Average temperature is {temp_data.mean():.1f}°C ± {temp_data.std():.1f}°C")
        print(f"• Data is sampled every {avg_interval.total_seconds()/60:.0f} minutes")
        print(f"• {len(outliers)} outlier measurements detected ({len(outliers)/len(df)*100:.1f}%)")
        print(f"• Temperature stability: ±{temp_stability:.2f}°C average change")
        print()
        
    except Exception as e:
        print(f"Error analyzing dataset: {e}")
        return None
    
    return analysis_results

def main():
    """Main analysis function"""
    
    # Path to the sensor data
    dataset_path = "/mnt/common/jcernudagarcia/demo/phase3/data/sensor_data.csv"
    
    # Perform analysis
    results = analyze_sensor_data_csv(dataset_path)
    
    if results:
        print("CSV analysis completed successfully!")
        return 0
    else:
        print("CSV analysis failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())