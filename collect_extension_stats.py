#!/usr/bin/env python3
"""
Collect Slicer extension download statistics for repos that are Slicer extensions.
This script identifies Slicer extensions from repos.json and generates a summary table.
"""

import json
import csv
import os
import sys

# Import the logic from extension_stats_summary.py
from extension_stats_summary import ExtensionStatsLogic


# Slicer extensions from repos.json based on naming patterns
# These are the repos that have "Slicer" prefix or are known extensions
SLICER_EXTENSION_MAP = {
    'SlicerMorph': 'SlicerMorph',
    'DeCA': 'DenseCorrespondenceAnalysis',
    'Photogrammetry': 'Photogrammetry',
    'MEMOs': 'SlicerMEMOs',  # Full extension name
    'ANTsPy': 'SlicerANTsPy',  # Full extension name
    'MorphoDepot': 'MorphoDepot',
    'ScriptEditor': 'ScriptEditor',
}


def identify_slicer_extensions(repos_file='repos.json'):
    """
    Identify which repositories are Slicer extensions.
    Matches repo names against actual extension names from Slicer server (case-insensitive).
    
    Returns:
        List of extension names to query
    """
    with open(repos_file, 'r') as f:
        repos_data = json.load(f)
    
    # Fetch all available extensions from the server
    print("Fetching list of all Slicer extensions...")
    logic = ExtensionStatsLogic()
    all_extensions = logic.getExtensionNames()
    
    # Create case-insensitive lookup
    extension_lookup = {ext.lower(): ext for ext in all_extensions}
    
    extension_names = []
    
    for repo in repos_data['repositories']:
        display_name = repo['display_name']
        repo_name = repo['name']
        
        # Skip non-extension repos
        if display_name in ['101_Course', '102_Course', 'Tutorials', 'MCI']:
            print(f"- Skipping non-extension: {display_name}")
            continue
        
        # Try to match against known extensions
        matched = False
        
        # First check if there's an explicit mapping
        if display_name in SLICER_EXTENSION_MAP:
            search_name = SLICER_EXTENSION_MAP[display_name]
            if search_name.lower() in extension_lookup:
                actual_name = extension_lookup[search_name.lower()]
                extension_names.append(actual_name)
                print(f"✓ Identified Slicer extension: {display_name} -> {actual_name}")
                matched = True
        
        # Try matching the display name directly (case-insensitive)
        if not matched and display_name.lower() in extension_lookup:
            actual_name = extension_lookup[display_name.lower()]
            extension_names.append(actual_name)
            print(f"✓ Identified Slicer extension: {display_name} -> {actual_name}")
            matched = True
        
        # Try matching the repo name (case-insensitive)
        if not matched and repo_name.lower() in extension_lookup:
            actual_name = extension_lookup[repo_name.lower()]
            extension_names.append(actual_name)
            print(f"✓ Identified Slicer extension: {repo_name} -> {actual_name}")
            matched = True
        
        # Try removing "Slicer" prefix and matching
        if not matched and repo_name.startswith('Slicer'):
            without_prefix = repo_name[6:]  # Remove "Slicer" prefix
            if without_prefix.lower() in extension_lookup:
                actual_name = extension_lookup[without_prefix.lower()]
                extension_names.append(actual_name)
                print(f"✓ Identified Slicer extension: {repo_name} -> {actual_name}")
                matched = True
        
        if not matched:
            print(f"- No matching extension found for: {display_name}")
    
    return extension_names


def create_markdown_table(csv_file='extension_stats.csv'):
    """
    Convert CSV to markdown table with only non-zero columns.
    Adds a Total Downloads column as the second column.
    
    Returns:
        String containing markdown table
    """
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    if len(rows) < 2:
        return "No extension statistics available.\n"
    
    header = rows[0]
    data_rows = rows[1:]
    
    # Calculate totals for each extension
    row_totals = []
    for row in data_rows:
        total = sum(int(val) for val in row[1:] if val.isdigit())
        row_totals.append(total)
    
    # Find columns with non-zero values (excluding the first column which is Extension Name)
    non_zero_columns = [0]  # Always include first column (Extension Name)
    for col_idx in range(1, len(header)):
        has_non_zero = False
        for row in data_rows:
            if col_idx < len(row) and row[col_idx] != '0':
                has_non_zero = True
                break
        if has_non_zero:
            non_zero_columns.append(col_idx)
    
    # Build markdown table with Total Downloads as second column
    md_lines = []
    header_row = [header[0], "Total Downloads"] + [header[i] for i in non_zero_columns[1:]]
    md_lines.append("| " + " | ".join(header_row) + " |")
    md_lines.append("|" + "|".join(["---" for _ in header_row]) + "|")
    
    for idx, row in enumerate(data_rows):
        values = [row[0], f"{row_totals[idx]:,}"]  # Extension name and total
        for col_idx in non_zero_columns[1:]:
            if col_idx < len(row):
                # Format numbers with commas for readability
                val = row[col_idx]
                if val.isdigit() and int(val) > 0:
                    values.append(f"{int(val):,}")
                else:
                    values.append(val)
            else:
                values.append('0')
        md_lines.append("| " + " | ".join(values) + " |")
    
    return "\n".join(md_lines) + "\n"


def update_readme(markdown_table, readme_file='README.md'):
    """
    Update README.md with the extension statistics table.
    """
    # Read current README
    with open(readme_file, 'r') as f:
        content = f.read()
    
    # Define the markers for the extension stats section
    start_marker = "## Slicer Extension Download Statistics"
    end_marker = "## How It Works"
    
    # Create the extension stats section
    extension_section = f"""{start_marker}

Weekly collection of download statistics for Slicer extensions from the [3D Slicer Extensions Index](https://slicer-packages.kitware.com).

### Download Statistics by Release

{markdown_table}

*Last updated: Automatically via GitHub Actions (weekly)*

"""
    
    # Check if section already exists
    if start_marker in content:
        # Replace existing section
        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker, start_idx)
        
        if end_idx == -1:
            # Section exists but no end marker found, append at the end
            print("Warning: Could not find end marker, appending to end")
            content = content[:start_idx] + extension_section
        else:
            content = content[:start_idx] + extension_section + "\n" + content[end_idx:]
    else:
        # Insert after "Tracked Repositories" section
        insert_marker = "## How It Works"
        if insert_marker in content:
            insert_idx = content.find(insert_marker)
            content = content[:insert_idx] + extension_section + "\n" + content[insert_idx:]
        else:
            # Just append to the end
            content += "\n\n" + extension_section
    
    # Write updated README
    with open(readme_file, 'w') as f:
        f.write(content)
    
    print(f"✓ Updated {readme_file} with extension statistics")


def main():
    """Main execution function."""
    print("="*80)
    print("Collecting Slicer Extension Download Statistics")
    print("="*80)
    
    # Identify Slicer extensions from repos.json
    extension_names = identify_slicer_extensions()
    
    if not extension_names:
        print("\nNo Slicer extensions found in repos.json")
        return 0
    
    print(f"\nCollecting statistics for {len(extension_names)} extension(s)...")
    
    # Create logic instance and fetch stats
    logic = ExtensionStatsLogic()
    extension_release_downloads = logic.getExtensionDownloadStats(extension_names)
    
    if not extension_release_downloads:
        print("Error: Could not retrieve extension statistics")
        return 1
    
    # Get all releases
    releases = logic.getSlicerReleaseNames()
    
    # Write to CSV
    csv_file = 'extension_stats.csv'
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(['Extension Name'] + releases)
        
        # Write data for each extension
        for extensionName in extension_names:
            if extensionName not in extension_release_downloads:
                print(f"Warning: No data found for extension '{extensionName}'")
                continue
            
            release_downloads = extension_release_downloads[extensionName]
            row = [extensionName]
            
            for release in releases:
                count = release_downloads.get(release, 0)
                row.append(count)
            
            writer.writerow(row)
    
    print(f"✓ CSV file written to: {csv_file}")
    
    # Create markdown table
    markdown_table = create_markdown_table(csv_file)
    
    # Update README.md
    update_readme(markdown_table)
    
    print("\n" + "="*80)
    print("Extension statistics collection complete!")
    print("="*80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
