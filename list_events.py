from config.events import EVENTS

if __name__ == "__main__":
    for key, meta in EVENTS.items():
        print(f"{key},{meta['type']}")
