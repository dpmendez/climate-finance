# declare dictionary of events
# each event is a dictionary with metadata
EVENTS = {
    "harvey_2017": {
        "name": "Hurricane Harvey",
        "type": "Hurricane",
        "event_date": "2017-08-25",
        "start_date": "2017-08-01",
        "end_date": "2017-09-15",
        "location": {"lat": 29.7604, "lon": -95.3698},  # Houston, TX
        "estimated_loss_usd": 125_000_000_000,
        "sectors_affected": ["Energy", "Insurance", "Construction"],
        "sector_tickers": {
            "SPY": "Index",
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLB": "Materials",
            "XLP": "Consumer Staples",
            "XLU": "Utilities",
            "XLF": "Financials",
            "XLRE": "Real Estate"}
    },
    "irma_2017": {
        "name": "Hurricane Irma",
        "type": "Hurricane",
        "event_date": "2017-09-10",
        "start_date": "2017-08-25",
        "end_date": "2017-09-20",
        "location": {"lat": 25.7617, "lon": -80.1918},  # Miami, FL
        "estimated_loss_usd": 50_000_000_000,
        "sectors_affected": ["Tourism", "Utilities", "Agriculture"]
    },
    "maria_2017": {
        "name": "Hurricane Maria",
        "type": "Hurricane",
        "event_date": "2017-09-20",
        "start_date": "2017-09-01",
        "end_date": "2017-10-15",
        "location": {"lat": 18.4655, "lon": -66.1057},  # San Juan, PR
        "estimated_loss_usd": 90_000_000_000,
        "sectors_affected": ["Infrastructure", "Healthcare", "Utilities"]
    },
    "wildfires_west_2020": {
        "name": "Western U.S. Wildfires",
        "type": "Wildfire",
        "event_date": "2020-09-01",
        "start_date": "2020-08-15",
        "end_date": "2020-10-15",
        "location": {"lat": 38.5816, "lon": -121.4944},  # Sacramento, CA
        "estimated_loss_usd": 16_500_000_000,
        "sectors_affected": ["Forestry", "Real Estate", "Insurance"]
    },
    "winter_storm_uri_2021": {
        "name": "Texas Winter Storm (Uri)",
        "type": "WinterStorm",
        "event_date": "2021-02-15",
        "start_date": "2021-02-01",
        "end_date": "2021-02-28",
        "location": {"lat": 30.2672, "lon": -97.7431},  # Austin, TX
        "estimated_loss_usd": 195_000_000_000,
        "sectors_affected": ["Energy", "Utilities", "Agriculture"]
    },
    "ida_2021": {
        "name": "Hurricane Ida",
        "type": "Hurricane",
        "event_date": "2021-08-29",
        "start_date": "2021-08-15",
        "end_date": "2021-09-15",
        "location": {"lat": 29.9511, "lon": -90.0715},  # New Orleans, LA
        "estimated_loss_usd": 75_000_000_000,
        "sectors_affected": ["Energy", "Transportation", "Insurance"]
    },
    "maui_2023": {
        "name": "Maui Wildfires",
        "type": "Wildfire",
        "event_date": "2023-08-08",
        "start_date": "2023-08-01",
        "end_date": "2023-08-31",
        "location": {"lat": 20.7984, "lon": -156.3319},  # Lahaina, Maui
        "estimated_loss_usd": 5_500_000_000,
        "sectors_affected": ["Tourism", "Real Estate", "Environment"]
    },
    "michael_2018": {
        "name": "Hurricane Michael",
        "type": "Hurricane",
        "event_date": "2018-10-10",
        "start_date": "2018-09-25",
        "end_date": "2018-10-20",
        "location": {"lat": 30.1588, "lon": -85.6602},  # Panama City, FL
        "estimated_loss_usd": 25_000_000_000,
        "sectors_affected": ["Agriculture", "Insurance", "Infrastructure"]
    },
    "louisiana_floods_2016": {
        "name": "Louisiana Floods",
        "type": "Flood",
        "event_date": "2016-08-12",
        "start_date": "2016-08-01",
        "end_date": "2016-08-31",
        "location": {"lat": 30.4515, "lon": -91.1871},  # Baton Rouge, LA
        "estimated_loss_usd": 10_000_000_000,
        "sectors_affected": ["Housing", "Agriculture", "Insurance"]
    },
    "kentucky_floods_2022": {
        "name": "Eastern Kentucky Floods",
        "type": "Flood",
        "event_date": "2022-07-28",
        "start_date": "2022-07-15",
        "end_date": "2022-08-15",
        "location": {"lat": 37.6456, "lon": -83.1141},  # Hazard, KY
        "estimated_loss_usd": 1_200_000_000,
        "sectors_affected": ["Housing", "Infrastructure", "Healthcare"]
    },
    "helene_2024": {
        "name": "Hurricane Helene",
        "type": "Hurricane",
        "event_date": "2024-09-25",
        "start_date": "2024-09-20",
        "end_date": "2024-10-05",
        "location": {"lat": 35.2271, "lon": -80.8431},  # Charlotte, NC
        "severity_rank": 11,
        "estimated_loss_usd": 60_000_000_000,
        "sectors_affected": ["Energy", "Insurance", "Transportation"]
    }
}