#!/bin/bash

# Run pooled analysis for each event type
for event_type in Hurricane Wildfire Flood WinterStorm; do
    echo "Running pooled analysis for $event_type"
    python run_analysis.py --event_type "$event_type"
done
