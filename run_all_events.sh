#!/bin/bash

# Initialize a temporary file to store event types
TMP_TYPES_FILE=$(mktemp)
EVENTS=$(python list_events.py)

# Loop over events and run single-event analysis
echo "$EVENTS" | while IFS=',' read -r event_key event_type
do
    echo "Running single-event analysis for $event_key ($event_type)"
    python run_analysis.py --mode single --event_key "$event_key"

    # Store the event_type for later (to get unique values)
    echo "$event_type" >> "$TMP_TYPES_FILE"
done

# Get unique event types and run cross-event analysis once for each
echo "Running cross-event analyses..."

# Sort and remove duplicates
sort "$TMP_TYPES_FILE" | uniq | while read -r unique_type
do
    echo "Running cross-event analysis for $unique_type"
    python run_analysis.py --mode cross --event_type "$unique_type"
done

# Cleanup
rm "$TMP_TYPES_FILE"
