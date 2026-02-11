import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import argparse
from dotenv import load_dotenv
from analysis import run_pooled_analysis

def main():

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Please set VISUAL_CROSSING_API_KEY in your .env file.")

    parser = argparse.ArgumentParser(description="Run climate-financial event analysis.")
    parser.add_argument('--event_type', type=str, required=True,
                        help='Event type to analyze: Hurricane, Wildfire, Flood, WinterStorm')

    args = parser.parse_args()
    run_pooled_analysis(args.event_type, api_key)

if __name__ == "__main__":
    main()