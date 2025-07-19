#!/usr/bin/env python3
"""
Analyze Sensor Data CSV file with temperature measurements
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

def analyze_sensor_data(csv_file_path):
    """Analyze sensor data CSV and generate comprehensive report"""
    
    results = {
        "dataset_info": {},
        "data_summary": {},
        "temporal_analysis": {},
        "statistical_analysis": {},
        "quality_assessment": {}
    }
    
    print(f"Analyzing sensor data: {csv_file_path}")
    
    try:
        # Load the CSV data
        df = pd.read_csv(csv_file_path)
        print(f"Loaded dataset with {len(df)} records and {len(df.columns)} columns")
        
        # Basic dataset information
        results["dataset_info"] = {
            "file_path": csv_file_path,
            "total_records": len(df),
            "columns": list(df.columns),
            "file_size_kb": round(len(open(csv_file_path, 'r').read()) / 1024, 2)
        }
        
        # Convert timestamp to datetime if it's not already
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Data summary
        results["data_summary"] = {
            "columns_info": {
                "timestamp": {
                    "type": "datetime",
                    "first_timestamp": df['timestamp'].min().isoformat(),
                    "last_timestamp": df['timestamp'].max().isoformat(),
                    "range": str(df['timestamp'].max() - df['timestamp'].min())
                },
                "sensor_value": {
                    "type": "numeric",
                    "unit": "°C (degrees Celsius)",
                    "data_type": str(df['sensor_value'].dtype)
                }
            }
        }
        
        # Temporal analysis
        time_diff = df['timestamp'].diff().dropna()
        results["temporal_analysis"] = {
            "measurement_interval": {
                "mode_minutes": int(time_diff.mode()[0].total_seconds() / 60),
                "mean_minutes": time_diff.mean().total_seconds() / 60,
                "std_minutes": time_diff.std().total_seconds() / 60,
                "is_regular": len(time_diff.unique()) == 1
            },
            "duration": {
                "total_duration": str(df['timestamp'].max() - df['timestamp'].min()),
                "total_hours": (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600,
                "total_days": (df['timestamp'].max() - df['timestamp'].min()).days
            }
        }
        
        # Statistical analysis
        temp_stats = df['sensor_value'].describe()
        results["statistical_analysis"] = {
            "temperature_statistics": {
                "count": int(temp_stats['count']),
                "mean": round(temp_stats['mean'], 2),
                "std": round(temp_stats['std'], 2),
                "min": round(temp_stats['min'], 2),
                "25th_percentile": round(temp_stats['25%'], 2),
                "median": round(temp_stats['50%'], 2),
                "75th_percentile": round(temp_stats['75%'], 2),
                "max": round(temp_stats['max'], 2),
                "range": round(temp_stats['max'] - temp_stats['min'], 2)
            },
            "temperature_distribution": {
                "variance": round(df['sensor_value'].var(), 2),
                "skewness": round(df['sensor_value'].skew(), 3),
                "kurtosis": round(df['sensor_value'].kurtosis(), 3)
            }
        }
        
        # Quality assessment
        missing_values = df.isnull().sum()
        duplicates = df.duplicated().sum()
        
        # Check for temperature anomalies (values beyond typical room temperature range)
        temp_values = df['sensor_value']
        anomaly_threshold_low = 15  # Below 15°C might be unusual for room temperature
        anomaly_threshold_high = 35  # Above 35°C might be unusual for room temperature
        
        low_anomalies = (temp_values < anomaly_threshold_low).sum()
        high_anomalies = (temp_values > anomaly_threshold_high).sum()
        
        results["quality_assessment"] = {
            "data_completeness": {
                "missing_timestamps": int(missing_values['timestamp']),
                "missing_sensor_values": int(missing_values['sensor_value']),
                "completeness_percentage": round((1 - missing_values.sum() / (len(df) * len(df.columns))) * 100, 2)
            },
            "data_integrity": {
                "duplicate_records": int(duplicates),
                "unique_timestamps": len(df['timestamp'].unique()),
                "timestamp_duplicates": len(df) - len(df['timestamp'].unique())
            },
            "anomaly_detection": {
                "low_temperature_anomalies": int(low_anomalies),
                "high_temperature_anomalies": int(high_anomalies),
                "total_anomalies": int(low_anomalies + high_anomalies),
                "anomaly_percentage": round((low_anomalies + high_anomalies) / len(df) * 100, 2),
                "threshold_low": anomaly_threshold_low,
                "threshold_high": anomaly_threshold_high
            }
        }
        
        # Additional temporal patterns
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day
        
        hourly_avg = df.groupby('hour')['sensor_value'].mean()
        daily_avg = df.groupby('day')['sensor_value'].mean()
        
        results["temporal_analysis"]["patterns"] = {
            "temperature_by_hour": {
                "min_hour": int(hourly_avg.idxmin()),
                "max_hour": int(hourly_avg.idxmax()),
                "min_temp": round(hourly_avg.min(), 2),
                "max_temp": round(hourly_avg.max(), 2),
                "hourly_variation": round(hourly_avg.max() - hourly_avg.min(), 2)
            },
            "temperature_trend": {
                "first_day_avg": round(daily_avg.iloc[0], 2) if len(daily_avg) > 0 else None,
                "last_day_avg": round(daily_avg.iloc[-1], 2) if len(daily_avg) > 0 else None,
                "overall_trend": "increasing" if len(daily_avg) > 1 and daily_avg.iloc[-1] > daily_avg.iloc[0] else "decreasing" if len(daily_avg) > 1 else "stable"
            }
        }
        
        print("Analysis completed successfully!")
        
    except Exception as e:
        results["error"] = f"Error analyzing sensor data: {str(e)}"
        print(f"Error: {e}")
    
    return results

def generate_sensor_report(analysis_results):
    """Generate a formatted report from sensor analysis results"""
    
    report = []
    report.append("# Sensor Data Analysis Report")
    report.append("=" * 40)
    
    # Dataset Information
    if "dataset_info" in analysis_results:
        report.append("\n## Dataset Information")
        info = analysis_results["dataset_info"]
        report.append(f"- File: {info.get('file_path', 'Unknown')}")
        report.append(f"- Total Records: {info.get('total_records', 'Unknown')}")
        report.append(f"- Columns: {', '.join(info.get('columns', []))}")
        report.append(f"- File Size: {info.get('file_size_kb', 'Unknown')} KB")
    
    # Data Summary
    if "data_summary" in analysis_results:
        report.append("\n## Data Summary")
        summary = analysis_results["data_summary"]
        
        if "columns_info" in summary:
            cols = summary["columns_info"]
            if "timestamp" in cols:
                ts_info = cols["timestamp"]
                report.append(f"- Time Range: {ts_info.get('first_timestamp', 'Unknown')} to {ts_info.get('last_timestamp', 'Unknown')}")
                report.append(f"- Duration: {ts_info.get('range', 'Unknown')}")
            
            if "sensor_value" in cols:
                sv_info = cols["sensor_value"]
                report.append(f"- Sensor Value Type: {sv_info.get('type', 'Unknown')}")
                report.append(f"- Unit: {sv_info.get('unit', 'Unknown')}")
    
    # Temporal Analysis
    if "temporal_analysis" in analysis_results:
        report.append("\n## Temporal Analysis")
        temporal = analysis_results["temporal_analysis"]
        
        if "measurement_interval" in temporal:
            interval = temporal["measurement_interval"]
            report.append(f"- Measurement Interval: {interval.get('mode_minutes', 'Unknown')} minutes")
            report.append(f"- Regular Intervals: {'Yes' if interval.get('is_regular', False) else 'No'}")
        
        if "duration" in temporal:
            duration = temporal["duration"]
            report.append(f"- Total Duration: {duration.get('total_duration', 'Unknown')}")
            report.append(f"- Total Hours: {duration.get('total_hours', 'Unknown'):.1f}")
        
        if "patterns" in temporal:
            patterns = temporal["patterns"]
            if "temperature_by_hour" in patterns:
                hourly = patterns["temperature_by_hour"]
                report.append(f"- Coolest Hour: {hourly.get('min_hour', 'Unknown')}:00 ({hourly.get('min_temp', 'Unknown')}°C)")
                report.append(f"- Warmest Hour: {hourly.get('max_hour', 'Unknown')}:00 ({hourly.get('max_temp', 'Unknown')}°C)")
                report.append(f"- Daily Temperature Variation: {hourly.get('hourly_variation', 'Unknown')}°C")
    
    # Statistical Analysis
    if "statistical_analysis" in analysis_results:
        report.append("\n## Statistical Analysis")
        stats = analysis_results["statistical_analysis"]
        
        if "temperature_statistics" in stats:
            temp_stats = stats["temperature_statistics"]
            report.append(f"- Mean Temperature: {temp_stats.get('mean', 'Unknown')}°C")
            report.append(f"- Standard Deviation: {temp_stats.get('std', 'Unknown')}°C")
            report.append(f"- Temperature Range: {temp_stats.get('min', 'Unknown')}°C - {temp_stats.get('max', 'Unknown')}°C")
            report.append(f"- Median Temperature: {temp_stats.get('median', 'Unknown')}°C")
        
        if "temperature_distribution" in stats:
            dist = stats["temperature_distribution"]
            report.append(f"- Variance: {dist.get('variance', 'Unknown')}")
            report.append(f"- Skewness: {dist.get('skewness', 'Unknown')}")
    
    # Quality Assessment
    if "quality_assessment" in analysis_results:
        report.append("\n## Data Quality Assessment")
        quality = analysis_results["quality_assessment"]
        
        if "data_completeness" in quality:
            completeness = quality["data_completeness"]
            report.append(f"- Data Completeness: {completeness.get('completeness_percentage', 'Unknown')}%")
            report.append(f"- Missing Values: {completeness.get('missing_timestamps', 0) + completeness.get('missing_sensor_values', 0)}")
        
        if "data_integrity" in quality:
            integrity = quality["data_integrity"]
            report.append(f"- Duplicate Records: {integrity.get('duplicate_records', 'Unknown')}")
            report.append(f"- Unique Timestamps: {integrity.get('unique_timestamps', 'Unknown')}")
        
        if "anomaly_detection" in quality:
            anomaly = quality["anomaly_detection"]
            report.append(f"- Temperature Anomalies: {anomaly.get('total_anomalies', 'Unknown')} ({anomaly.get('anomaly_percentage', 'Unknown')}%)")
            report.append(f"- Anomaly Thresholds: {anomaly.get('threshold_low', 'Unknown')}°C - {anomaly.get('threshold_high', 'Unknown')}°C")
    
    if "error" in analysis_results:
        report.append(f"\n## Error\n{analysis_results['error']}")
    
    return "\n".join(report)

def main():
    # Analyze the sensor data
    csv_file = "/mnt/common/jcernudagarcia/demo/phase3/data/sensor_data.csv"
    
    print("Starting sensor data analysis...")
    results = analyze_sensor_data(csv_file)
    
    # Generate report
    report = generate_sensor_report(results)
    print("\n" + "="*50)
    print("SENSOR DATA ANALYSIS REPORT")
    print("="*50)
    print(report)
    
    # Save detailed results as JSON
    with open("/mnt/common/jcernudagarcia/demo/phase3/sensor_data_analysis.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed analysis saved to: sensor_data_analysis.json")
    
    return results, report

if __name__ == "__main__":
    main()