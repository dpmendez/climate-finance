import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import argparse
from dotenv import load_dotenv
from analysis import run_event_analysis, run_cross_event_analysis
from config.events import EVENTS

def main():

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Please set VISUAL_CROSSING_API_KEY in your .env file.")

    # Command-line argument for event selection
    # Command-line arguments
    parser = argparse.ArgumentParser(description="Run climate-financial event analysis.")
    parser.add_argument('--mode', type=str, default='single', choices=['single', 'cross'],
                        help='Type of analysis to run: single event or cross-event.')
    parser.add_argument('--event_key', type=str, choices=EVENTS.keys(),
                        help='Event key from config/events.py (required for single-event mode).')
    parser.add_argument('--event_type', type=str,
                        help='Event type to filter for cross-event analysis (e.g., Hurricane, Wildfire, Flood).')

    args = parser.parse_args()

    if args.mode == 'single':
        if not args.event_key:
            raise ValueError("Please provide an event key for single-event mode.")
        run_event_analysis(args.event_key, api_key)

    elif args.mode == 'cross':
        if not args.event_type:
            raise ValueError("Please provide an event type (e.g., Hurricane, Wildfire) for cross-event mode.")
        run_cross_event_analysis(args.event_type, api_key)

if __name__ == "__main__":
    main()