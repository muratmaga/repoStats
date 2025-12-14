#!/usr/bin/env python3
"""
Simplified script to create a summary table for Slicer extensions.
Based on ExtensionStats.py from Slicer/SlicerDeveloperToolsForExtensions

Usage:
    python extension_stats_summary.py --extensions SlicerMorph,Photogrammetry --output summary.csv
"""

import argparse
import csv
import json
import requests
import sys


class ExtensionStatsLogic:
    """Logic to retrieve and process Slicer extension download statistics."""
    
    def __init__(self):
        self.postReleasePrefix = "post-"
        
        # Slicer release versions with their revision and release date
        # Format: 'version': ['revision', 'date']
        releases_revisionsDates = {
            '4.0.0': ['18777', '2011-11-27'],
            '4.0.1': ['19033', '2012-01-06'],
            '4.1.0': ['19886', '2012-04-12'],
            '4.1.1': ['20313', '2012-06-01'],
            '4.2.0': ['21298', '2012-10-31'],
            '4.2.1': ['21438', '2012-11-16'],
            '4.2.2': ['21508', '2012-12-07'],
            '4.2.2-1': ['21513', '2012-12-08'],
            '4.3.0': ['22408', '2013-09-04'],
            '4.3.1': ['22599', '2013-10-04'],
            '4.3.1-1': ['22704', '2013-11-14'],
            '4.4.0': ['23774', '2014-11-02'],
            '4.5.0-1': ['24735', '2015-11-12'],
            '4.6.0': ['25441', '2016-10-13'],
            '4.6.2': ['25516', '2016-11-08'],
            '4.8.0': ['26489', '2017-10-18'],
            '4.8.1': ['26813', '2017-12-19'],
            '4.10.0': ['27510', '2018-10-17'],
            '4.10.1': ['27931', '2019-01-15'],
            '4.10.2': ['28257', '2019-05-16'],
            '4.11.20200930': ['29402', '2020-09-30'],
            '4.11.20210226': ['29738', '2021-02-26'],
            '5.0.2': ['30822', '2022-05-06'],
            '5.0.3': ['30893', '2022-07-08'],
            '5.2.1': ['31317', '2022-11-24'],
            '5.2.2': ['31382', '2023-02-21'],
            '5.4.0': ['31938', '2023-08-19'],
            '5.6.0': ['32390', '2023-11-16'],
            '5.6.1': ['32438', '2023-12-12'],
            '5.6.2': ['32448', '2024-04-05'],
            '5.8.0': ['33216', '2025-01-24'],
            '5.8.1': ['33241', '2025-03-02'],
            '5.10.0': ['34045', '2025-11-10'],
        }
        
        # Sort releases based on SVN revision
        self.releases_revisionsDates = sorted(releases_revisionsDates.items(), key=lambda t: t[1])
        
        self.legacyReleaseName = "legacy"
        self.unknownReleaseName = "unknown"
        
        # URL to fetch download statistics from Slicer extensions server
        self.downloadstatsUrl = "https://slicer-packages.kitware.com/api/v1/app/5f4474d0e1d8c75dfc705482/downloadstats"
        self.downloadstats = None
    
    def getSlicerReleaseNames(self):
        """Return sorted list of release names."""
        releases = [self.unknownReleaseName, self.legacyReleaseName]
        for releaseRevision in self.releases_revisionsDates:
            releases.append(releaseRevision[0])
            releases.append(self.postReleasePrefix + releaseRevision[0])
        return releases
    
    def getSlicerReleaseName(self, revision):
        """
        Return Slicer release name that corresponds to a Slicer revision.
        Downloads associated with nightly builds between releases A and B are
        associated with post-A "release".
        """
        try:
            revision = int(revision)
        except ValueError:
            return self.unknownReleaseName
        
        release = self.legacyReleaseName
        for release_revisionDate in self.releases_revisionsDates:
            if revision < int(release_revisionDate[1][0]):
                break
            if revision == int(release_revisionDate[1][0]):
                # Exact match to a release
                release = release_revisionDate[0]
                break
            release = self.postReleasePrefix + release_revisionDate[0]
        
        return release
    
    def getExtensionDownloadStats(self, extensionNames=None):
        """
        Return download count for extensions in a map indexed by extensionName and release.
        
        Args:
            extensionNames: list containing extension names to consider,
                          or None to get statistics for all extensions.
        
        Returns:
            Dictionary: {extensionName: {release: downloadCount}}
        """
        extension_release_downloads = {}
        
        # Fetch current extension download stats from Extensions Server
        if self.downloadstats is None:
            print("Fetching download statistics from server...")
            try:
                resp = requests.get(self.downloadstatsUrl, timeout=30)
                resp.raise_for_status()
                self.downloadstats = resp.json()
                print(f"Successfully retrieved statistics for {len(self.downloadstats)} revisions")
            except Exception as e:
                print(f"Error fetching download stats: {e}")
                return extension_release_downloads
        
        # Process download statistics
        for revision in self.downloadstats:
            release = self.getSlicerReleaseName(revision)
            
            if 'extensions' not in self.downloadstats[revision]:
                # No extensions downloaded for this release
                continue
            
            for extensionName in self.downloadstats[revision]['extensions']:
                if extensionNames and (extensionName not in extensionNames):
                    # This extension is not in the requested list
                    continue
                
                # Sum downloads across all platforms
                downloadCount = 0
                platforms = ['win', 'macosx', 'linux']
                architectures = ['amd64', 'arm64']
                
                for platform in platforms:
                    for arch in architectures:
                        try:
                            downloadCount += self.downloadstats[revision]['extensions'][extensionName][platform][arch]
                        except (KeyError, TypeError):
                            pass
                
                if downloadCount == 0:
                    continue
                
                # Initialize extension entry if needed
                if extensionName not in extension_release_downloads:
                    extension_release_downloads[extensionName] = {}
                
                # Initialize release entry if needed
                if release not in extension_release_downloads[extensionName]:
                    extension_release_downloads[extensionName][release] = 0
                
                # Add to total
                extension_release_downloads[extensionName][release] += downloadCount
        
        return extension_release_downloads
    
    def getExtensionNames(self):
        """Get list of all available extension names."""
        extension_release_downloads = self.getExtensionDownloadStats()
        return sorted(list(extension_release_downloads.keys()))


def create_summary_table(extension_names, output_format='csv', output_file=None):
    """
    Create a summary table for specified extensions.
    
    Args:
        extension_names: List of extension names to query
        output_format: 'csv', 'json', or 'console'
        output_file: Output file path (optional)
    """
    logic = ExtensionStatsLogic()
    
    # Get download statistics
    print(f"Retrieving statistics for extensions: {', '.join(extension_names)}")
    extension_release_downloads = logic.getExtensionDownloadStats(extension_names)
    
    if not extension_release_downloads:
        print("No download statistics found for the specified extensions.")
        return
    
    # Get all releases
    releases = logic.getSlicerReleaseNames()
    
    # Output based on format
    if output_format == 'json':
        output_data = extension_release_downloads
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"JSON output written to: {output_file}")
        else:
            print(json.dumps(output_data, indent=2))
    
    elif output_format == 'csv':
        if output_file:
            with open(output_file, 'w', newline='') as csvfile:
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
            
            print(f"CSV output written to: {output_file}")
        else:
            # Print to console
            print("\n" + "="*80)
            print(f"{'Extension Name':<20} | {'Total Downloads':>15}")
            print("="*80)
            
            for extensionName in extension_names:
                if extensionName not in extension_release_downloads:
                    print(f"Warning: No data found for extension '{extensionName}'")
                    continue
                
                release_downloads = extension_release_downloads[extensionName]
                total = sum(release_downloads.values())
                print(f"{extensionName:<20} | {total:>15,}")
            
            print("="*80)
            
            # Print detailed breakdown
            print("\nDetailed breakdown by release:")
            print("-"*80)
            for extensionName in extension_names:
                if extensionName not in extension_release_downloads:
                    continue
                
                print(f"\n{extensionName}:")
                release_downloads = extension_release_downloads[extensionName]
                
                # Sort releases by download count
                sorted_releases = sorted(release_downloads.items(), 
                                       key=lambda x: x[1], reverse=True)
                
                for release, count in sorted_releases[:10]:  # Show top 10
                    if count > 0:
                        print(f"  {release:<20}: {count:>8,}")


def main():
    parser = argparse.ArgumentParser(
        description='Create summary table for Slicer extension download statistics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate summary for SlicerMorph and Photogrammetry (console output)
  python %(prog)s --extensions SlicerMorph,Photogrammetry
  
  # Save to CSV file
  python %(prog)s --extensions SlicerMorph,Photogrammetry --output summary.csv
  
  # Save to JSON file
  python %(prog)s --extensions SlicerMorph,Photogrammetry --output summary.json
  
  # List all available extensions
  python %(prog)s --list-extensions
        """
    )
    
    parser.add_argument(
        '-e', '--extensions',
        dest='extensions',
        help='Comma-separated list of extension names (e.g., SlicerMorph,Photogrammetry)'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='Output file path (.csv or .json)'
    )
    
    parser.add_argument(
        '-l', '--list-extensions',
        action='store_true',
        help='List all available extensions'
    )
    
    args = parser.parse_args()
    
    # List extensions if requested
    if args.list_extensions:
        print("Fetching list of all available extensions...")
        logic = ExtensionStatsLogic()
        extensions = logic.getExtensionNames()
        print(f"\nFound {len(extensions)} extensions:")
        for ext in extensions:
            print(f"  - {ext}")
        return 0
    
    # Validate arguments
    if not args.extensions:
        parser.error("--extensions is required (or use --list-extensions to see available extensions)")
    
    # Parse extension names
    extension_names = [name.strip() for name in args.extensions.split(',')]
    
    # Determine output format
    if args.output_file:
        if args.output_file.endswith('.json'):
            output_format = 'json'
        elif args.output_file.endswith('.csv'):
            output_format = 'csv'
        else:
            print("Warning: Output file should have .csv or .json extension. Defaulting to CSV.")
            output_format = 'csv'
    else:
        output_format = 'csv'
    
    # Create summary table
    try:
        create_summary_table(extension_names, output_format, args.output_file)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
