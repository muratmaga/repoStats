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
| SlicerMorph | 46,472 | 306 | 2,768 | 5,981 | 984 | 1,828 | 1,275 | 1,245 | 2,773 | 1,278 | 2,086 | 380 | 441 | 2,514 | 5,556 | 3,657 | 1,191 | 5,924 | 1,342 | 4,545 | 398 |
| DenseCorrespondenceAnalysis | 1,497 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 457 | 408 | 550 | 82 |
| Photogrammetry | 701 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 68 | 342 | 270 | 9 |
| MEMOS | 6,473 | 0 | 0 | 0 | 0 | 0 | 0 | 77 | 443 | 651 | 322 | 187 | 82 | 279 | 500 | 2,826 | 94 | 357 | 389 | 220 | 46 |
| SlicerANTsPy | 1,144 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 494 | 165 | 402 | 83 |
| MorphoDepot | 2,137 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 183 | 92 | 477 | 680 | 627 | 78 |
| ScriptEditor | 3,371 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 417 | 800 | 229 | 1,009 | 314 | 499 | 103 |


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
