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
| SlicerMorph | 43,492 | 302 | 2,763 | 5,981 | 978 | 1,822 | 1,275 | 1,238 | 2,749 | 1,278 | 2,063 | 380 | 439 | 2,489 | 5,493 | 3,628 | 1,173 | 5,669 | 1,324 | 2,254 | 194 |
| DenseCorrespondenceAnalysis | 1,121 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 435 | 407 | 244 | 35 |
| Photogrammetry | 536 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 11 | 67 | 342 | 114 | 2 |
| MEMOS | 6,287 | 0 | 0 | 0 | 0 | 0 | 0 | 77 | 440 | 651 | 319 | 187 | 81 | 279 | 490 | 2,795 | 90 | 348 | 389 | 125 | 16 |
| SlicerANTsPy | 901 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 467 | 162 | 233 | 39 |
| MorphoDepot | 1,723 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 183 | 88 | 462 | 680 | 271 | 39 |
| ScriptEditor | 3,018 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 406 | 772 | 225 | 976 | 313 | 270 | 56 |


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
