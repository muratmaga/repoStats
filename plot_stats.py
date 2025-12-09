import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime

def parse_concatenated_json(file_path):
    """Parse concatenated JSON objects from file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Split by }{ and add back the braces
    json_strings = content.split('}{')
    json_objects = []
    
    for i, s in enumerate(json_strings):
        if i == 0:
            s = s + '}'
        elif i == len(json_strings) - 1:
            s = '{' + s
        else:
            s = '{' + s + '}'
        
        try:
            json_objects.append(json.loads(s))
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON segment {i}: {e}")
            continue
    
    return json_objects

def create_views_plot(repo_data, repo_name, output_path):
    """Create a views plot for a repository."""
    all_views = []
    for record in repo_data:
        if 'views' in record:
            for view in record['views']:
                all_views.append({
                    'date': pd.to_datetime(view['timestamp']).date(),
                    'count': view['count'],
                    'uniques': view['uniques']
                })
    
    if not all_views:
        print(f"No data found for {repo_name}")
        return
    
    df = pd.DataFrame(all_views)
    
    # Remove duplicates, keeping the last entry for each date
    df = df.groupby('date').tail(1).reset_index(drop=True)
    
    # Sort by date
    df = df.sort_values('date')
    
    # Create plot with larger size
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot views and uniques with thicker lines and larger markers
    ax.plot(df['date'], df['count'], marker='o', linewidth=2.5, 
            markersize=6, label='Views', color='#2E86AB')
    ax.plot(df['date'], df['uniques'], marker='s', linewidth=2.5, 
            markersize=6, label='Unique Visitors', color='#A23B72')
    
    # Format x-axis with larger font
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Labels and title with larger fonts
    ax.set_xlabel('Date', fontsize=14, fontweight='bold')
    ax.set_ylabel('Count', fontsize=14, fontweight='bold')
    ax.set_title(f'{repo_name} - Traffic Statistics', fontsize=18, fontweight='bold', pad=20)
    
    # Grid and legend with larger font
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(fontsize=11, frameon=True, shadow=True)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save with high DPI for better quality
    plt.savefig(output_path, format='svg', dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Generated plot for {repo_name}: {output_path}")

def main():
    # Load repository configuration
    with open('repos.json', 'r') as f:
        config = json.load(f)
        repos = config['repositories']
    
    # Create graphs directory
    graphs_dir = Path('graphs')
    graphs_dir.mkdir(exist_ok=True)
    
    # Process each repository
    for repo in repos:
        display_name = repo['display_name']
        json_file = f"{display_name}.json"
        
        if not Path(json_file).exists():
            print(f"Warning: {json_file} not found, skipping...")
            continue
        
        # Parse data
        repo_data = parse_concatenated_json(json_file)
        
        # Generate plot
        output_file = graphs_dir / f"{display_name.lower()}_views.svg"
        create_views_plot(repo_data, display_name, output_file)

if __name__ == '__main__':
    main()
