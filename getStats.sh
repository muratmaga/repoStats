#!/bin/bash
cd /home/maga/repoStats

gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/SlicerMorph/Tutorials/traffic/views >> Tutorials.json
  
gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/SlicerMorph/SlicerMorph/traffic/views >> SlicerMorph.json

gh api \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/MorphoCloud/MorphoCloudInstances/traffic/views >> MCI.json

git add *.json
git commit -m "new stats"
git push origin main