#!/usr/bin/env python3
"""
Plot repository statistics from GitHub traffic data.
Reads repository configuration from repos.json and generates views plots.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path


def load_repo_config(config_file='repos.json'):
    """Load repository configuration from JSON file."""
    with open(config_file, 'r') as f:
        config = json.load(f)
    return config['repositories']


def parse_concatenated_json(json_file):
    """
    Parse concatenated JSON objects from a file.
    The file contains multiple JSON objects appended together like: }{
    
    Args:
        json_file: Path to JSON file
        
    Returns:
        pandas.DataFrame with all views data combined
    """
    with open(json_file, 'r') as f:
        json_text = f.read()
    
    # Split by "}{" to separate multiple JSON objects
    json_objects = json_text.split("}{")
    
    # Reconstruct each JSON object by adding back the braces
    reconstructed = []
    for i, obj in enumerate(json_objects):
        if i == 0:
            reconstructed.append(obj + "}")
        elif i == len(json_objects) - 1:
            reconstructed.append("{" + obj)
        else:
            reconstructed.append("{" + obj + "}")
    
    # Parse all JSON objects and combine the views
    all_views = []
    for json_str in reconstructed:
        try:
            data_obj = json.loads(json_str)
            if 'views' in data_obj:
                all_views.extend(data_obj['views'])
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse JSON object: {e}")
            continue
    
    # Convert to DataFrame
    df = pd.DataFrame(all_views)
    
    if df.empty:
        return df
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    
    # Remove duplicate dates (keep the most recent data for each date)
    df = df.sort_values('timestamp').groupby('date').tail(1).reset_index(drop=True)
    
    return df


def create_views_plot(df, repo_name, output_file):
    """
    Create a views plot showing total views and unique visitors over time.
    
    Args:
        df: DataFrame with views data
        repo_name: Name of the repository for the title
        output_file: Output filename for the SVG
    """
    # Calculate cumulative totals and averages
    total_views = df['count'].sum()
    total_uniques = df['uniques'].sum()
    avg_daily_views = df['count'].mean()
    avg_daily_uniques = df['uniques'].mean()
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot lines and points
    ax.plot(df['date'], df['count'], color='#2E86AB', linewidth=1.5, 
            marker='o', markersize=4, 
            label=f'Total Views (Cumulative: {total_views:,})')
    ax.plot(df['date'], df['uniques'], color='#A23B72', linewidth=1.5, 
            marker='o', markersize=4,
            label=f'Unique Visitors (Cumulative: {total_uniques:,})')
    
    # Add average lines
    ax.axhline(y=avg_daily_views, color='#2E86AB', linestyle='--', 
               linewidth=1.2, alpha=0.7,
               label=f'Avg Total Views ({avg_daily_views:.1f})')
    ax.axhline(y=avg_daily_uniques, color='#A23B72', linestyle='--', 
               linewidth=1.2, alpha=0.7,
               label=f'Avg Unique Visitors ({avg_daily_uniques:.1f})')
    
    # Format the plot
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Number of Views', fontsize=11)
    ax.set_title(f'{repo_name} Repository Views Over Time', 
                 fontsize=14, fontweight='bold', pad=10)
    
    # Add subtitle
    fig.text(0.125, 0.915, 
             f'Total: {total_views:,} views from {total_uniques:,} unique visitors',
             fontsize=10, color='#555')
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add legend
    ax.legend(loc='upper left', fontsize=9, frameon=True, fancybox=False)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save as SVG
    plt.savefig(output_file, format='svg', bbox_inches='tight', dpi=300)
    plt.close()
    
    return total_views, total_uniques, avg_daily_views, avg_daily_uniques


def print_statistics(repo_name, df, total_views, total_uniques, avg_daily_views, avg_daily_uniques):
    """Print summary statistics for a repository."""
    print(f"\n{'='*50}")
    print(f"=== {repo_name} Repository Statistics Summary ===")
    print(f"{'='*50}")
    print(f"Total Views: {total_views:,}")
    print(f"Unique Visitors: {total_uniques:,}")
    print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"Average Daily Views: {avg_daily_views:.1f}")
    print(f"Average Daily Unique Visitors: {avg_daily_uniques:.1f}")
    
    max_views_idx = df['count'].idxmax()
    max_uniques_idx = df['uniques'].idxmax()
    print(f"Peak Daily Views: {df.loc[max_views_idx, 'count']} (on {df.loc[max_views_idx, 'date']})")
    print(f"Peak Daily Unique Visitors: {df.loc[max_uniques_idx, 'uniques']} (on {df.loc[max_uniques_idx, 'date']})")


def main():
    """Main function to process all repositories."""
    # Create graphs directory if it doesn't exist
    graphs_dir = Path('graphs')
    graphs_dir.mkdir(exist_ok=True)
    
    # Load repository configuration
    try:
        repos = load_repo_config()
        print(f"Loaded configuration for {len(repos)} repositories")
    except FileNotFoundError:
        print("Error: repos.json not found!")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing repos.json: {e}")
        return
    
    # Process each repository
    for repo in repos:
        display_name = repo['display_name']
        full_name = f"{repo['owner']}/{repo['name']}"
        json_file = f"{display_name}.json"
        output_file = graphs_dir / f"{display_name.lower()}_views.svg"
        
        print(f"\n{'='*50}")
        print(f"Processing {full_name}...")
        print(f"{'='*50}")
        
        # Check if data file exists
        if not Path(json_file).exists():
            print(f"Warning: {json_file} not found. Skipping...")
            continue
        
        # Parse JSON data
        df = parse_concatenated_json(json_file)
        
        if df.empty:
            print(f"Warning: No data found in {json_file}. Skipping...")
            continue
        
        # Create plot
        stats = create_views_plot(df, display_name, output_file)
        
        # Print statistics
        print_statistics(display_name, df, *stats)
        
        print(f"\n✓ Plot saved as: {output_file}")
    
    print(f"\n{'='*50}")
    print("All plots generated successfully!")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    main()
