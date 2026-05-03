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
| SlicerMorph | 46,023 | 305 | 2,766 | 5,981 | 984 | 1,827 | 1,275 | 1,245 | 2,771 | 1,278 | 2,081 | 380 | 441 | 2,511 | 5,550 | 3,646 | 1,188 | 5,887 | 1,338 | 4,205 | 364 |
| DenseCorrespondenceAnalysis | 1,450 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 455 | 408 | 509 | 78 |
| Photogrammetry | 692 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 68 | 342 | 261 | 9 |
| MEMOS | 6,439 | 0 | 0 | 0 | 0 | 0 | 0 | 77 | 443 | 651 | 322 | 187 | 82 | 279 | 497 | 2,814 | 94 | 357 | 389 | 202 | 45 |
| SlicerANTsPy | 1,109 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 487 | 164 | 379 | 79 |
| MorphoDepot | 2,090 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 183 | 92 | 474 | 680 | 590 | 71 |
| ScriptEditor | 3,305 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 415 | 788 | 229 | 1,004 | 314 | 459 | 96 |


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
