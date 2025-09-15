#!/bin/bash

# Get the current week number
WEEK_NUM=$(date +%W)

# Check if the week number is even or odd (adjust as needed for your desired starting Sunday)
# For odd numbered weeks:
if (( WEEK_NUM % 2 != 0 )); then
    /home/maga/repoStats/getStats.sh
fi
