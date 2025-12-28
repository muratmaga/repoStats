# Repository Traffic Statistics

Automated collection and visualization of GitHub repository traffic statistics.

## Tracked Repositories

Traffic statistics are collected weekly for the following repositories:

- **SlicerMorph/SlicerMorph**
- **SlicerMorph/Tutorials**
- **MorphoCloud/MorphoCloudInstances**

## Slicer Extension Download Statistics

Weekly collection of download statistics for Slicer extensions from the [3D Slicer Extensions Index](https://slicer-packages.kitware.com).

### Download Statistics by Release

| Extension Name | Total Downloads | 4.11.20200930 | 4.11.20210226 | post-4.11.20210226 | 5.0.2 | 5.0.3 | post-5.0.3 | 5.2.1 | 5.2.2 | post-5.2.2 | 5.4.0 | post-5.4.0 | 5.6.0 | 5.6.1 | 5.6.2 | post-5.6.2 | 5.8.0 | 5.8.1 | post-5.8.1 | 5.10.0 | post-5.10.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SlicerMorph | 41,703 | 297 | 2,747 | 5,981 | 976 | 1,817 | 1,275 | 1,230 | 2,731 | 1,278 | 2,051 | 380 | 435 | 2,480 | 5,410 | 3,507 | 1,150 | 5,513 | 1,300 | 1,047 | 98 |
| DenseCorrespondenceAnalysis | 966 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 426 | 406 | 120 | 14 |
| Photogrammetry | 468 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10 | 67 | 342 | 47 | 2 |
| MEMOS | 6,029 | 0 | 0 | 0 | 0 | 0 | 0 | 77 | 432 | 651 | 317 | 187 | 81 | 278 | 490 | 2,658 | 79 | 341 | 377 | 56 | 5 |
| SlicerANTsPy | 747 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 446 | 153 | 131 | 17 |
| MorphoDepot | 1,483 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 127 | 79 | 452 | 665 | 137 | 23 |
| ScriptEditor | 2,671 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 403 | 639 | 214 | 952 | 297 | 143 | 23 |


*Last updated: Automatically via GitHub Actions (weekly)*


## How It Works

### Data Collection

GitHub Actions runs weekly (every Sunday) to:
1. Fetch traffic data from GitHub's API (14-day rolling window)
2. Append the data to JSON files in this repository
3. Commit and push the updates automatically

### Adding New Repositories

To track additional repositories, simply edit `repos.json`:

```json
{
  "repositories": [
    {
      "owner": "YourOrg",
      "name": "YourRepo",
      "display_name": "YourRepo"
    }
  ]
}
```

**Fields:**
- `owner`: GitHub organization or user name
- `name`: Repository name
- `display_name`: Name used for output files (creates `{display_name}.json`)

The workflow will automatically start collecting data for new repositories on the next run.

### Visualization

Run the Python script to generate SVG graphs:

```bash
python3 plot_stats.py
```

This creates graphs in the `graphs/` directory showing:
- Total views over time
- Unique visitors over time
- Average daily metrics
- Cumulative statistics

## Data Files

- `repos.json` - Configuration file listing repositories to track
- `*.json` - Historical traffic data (concatenated GitHub API responses)
- `graphs/*.svg` - Generated visualization plots

## GitHub Pages

Visualizations are automatically deployed to GitHub Pages at:
- https://muratmaga.github.io/repoStats/

(Or https://slicermorph.github.io/usage_stats/ after migration)

## Requirements

For local development:
```bash
pip install pandas matplotlib
```

## Manual Data Collection

To manually collect stats:
```bash
# In GitHub Actions: workflow_dispatch trigger
# Or locally with gh CLI:
gh workflow run collect-stats.yml
```

## Technical Details

- **Collection Frequency**: Weekly (Sundays at 00:00 UTC)
- **Data Retention**: GitHub's API provides 14-day rolling windows
- **Storage**: JSON files are appended, not overwritten (full history preserved)
- **File Size**: ~500 bytes per repository per week (~78 KB/year for 3 repos)
