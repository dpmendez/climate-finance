import os
import argparse
from dotenv import load_dotenv
from src.analysis import run_event_analysis
from config.events import EVENTS

def main():
    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("VISUAL_CROSSING_API_KEY")

    if not api_key:
        raise ValueError("API key not found. Please set VISUAL_CROSSING_API_KEY in your .env file.")

    # Command-line argument for event selection
    parser = argparse.ArgumentParser(description="Run climate-financial event analysis.")
    parser.add_argument('--event_key', type=str, required=True,
                        choices=EVENTS.keys(),
                        help='Event key from config/events.py')
    args = parser.parse_args()

    run_event_analysis(args.event_key, api_key)

if __name__ == "__main__":
    main()
