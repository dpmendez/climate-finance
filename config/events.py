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
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLB": "Materials",
            "XLP": "Consumer Staples",
            "XLU": "Utilities",
            "XLF": "Financials",
            "XLRE": "Real Estate"},
        "regional_etfs": {
            "SMEZ": "MidCap Energy", # S&P MidCap 400 Equal Weight Energy (Texas-heavy energy exposure)
            "KRE": "Regional Banks" # Regional Banks ETF (many TX banks)
            }
        },
    "irma_2017": {
        "name": "Hurricane Irma",
        "type": "Hurricane",
        "event_date": "2017-09-10",
        "start_date": "2017-08-25",
        "end_date": "2017-09-20",
        "location": {"lat": 25.7617, "lon": -80.1918},  # Miami, FL
        "index": "SPY",
        "sector_etfs": {
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLF": "Financials",
            "JETS": "Airlines"
        },
        "regional_etfs": {
            "XLF": "Financial Select Sector", # Financial Select Sector SPDR (strong Florida bank exposure)
            "IYF": "iShares Financials" # iShares U.S. Financials ETF (regional bank exposure)
        }
    },
    "maria_2017": {
        "name": "Hurricane Maria",
        "type": "Hurricane",
        "event_date": "2017-09-20",
        "start_date": "2017-09-01",
        "end_date": "2017-10-15",
        "location": {"lat": 18.4655, "lon": -66.1057},  # San Juan, PR
        "index": "SPY",
        "sector_etfs": {
            "XLU": "Utilities", 
            "XLV": "Healthcare",
            "KIE": "Insurance",
            "XLP": "Consumer Staples",
            "XLI": "Industrials"
        },
        "regional_etfs": {}
    },
    "wildfires_west_2020": {
        "name": "Western U.S. Wildfires",
        "type": "Wildfire",
        "event_date": "2020-09-01",
        "start_date": "2020-08-15",
        "end_date": "2020-10-15",
        "location": {"lat": 38.5816, "lon": -121.4944},  # Sacramento, CA
        "index": "SPY",
        "sector_etfs": {
            "XLRE": "Real State",
            "XLB": "Materials",
            "ICLN": "Clean Energy",
            "XLE": "Energy",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "QCN": "Global Clean Energy", # Global Clean Energy ETF (large CA exposure)
            "IYW": "Technology Select Sector" # Technology Select Sector SPDR (strong West Coast tech exposure)
        }
    },
    "winter_storm_uri_2021": {
        "name": "Texas Winter Storm (Uri)",
        "type": "WinterStorm",
        "event_date": "2021-02-15",
        "start_date": "2021-02-01",
        "end_date": "2021-02-28",
        "location": {"lat": 30.2672, "lon": -97.7431},  # Austin, TX
        "index": "SPY",
        "sector_etfs": {
            "XLU": "Utilities",
            "XLE": "Energy",
            "XLP": "Consumer Staples",
            "XLF": "Financials",
            "IYT": "Transports"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    "ida_2021": {
        "name": "Hurricane Ida",
        "type": "Hurricane",
        "event_date": "2021-08-29",
        "start_date": "2021-08-15",
        "end_date": "2021-09-15",
        "location": {"lat": 29.9511, "lon": -90.0715},  # New Orleans, LA
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLI": "Industrials",
            "XLU": "Utilities",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    "maui_2023": {
        "name": "Maui Wildfires",
        "type": "Wildfire",
        "event_date": "2023-08-08",
        "start_date": "2023-08-01",
        "end_date": "2023-08-31",
        "location": {"lat": 20.7984, "lon": -156.3319},  # Lahaina, Maui
        "index": "SPY",
        "sector_etfs": {
            "XLRE": "Real State",
            "XLY": "Consumer Discretionary",
            "JETS": "Airlines",
            "KIE": "Insurance"
        },
        "regional_etfs": {}
    },
    "michael_2018": {
        "name": "Hurricane Michael",
        "type": "Hurricane",
        "event_date": "2018-10-10",
        "start_date": "2018-09-25",
        "end_date": "2018-10-20",
        "location": {"lat": 30.1588, "lon": -85.6602},  # Panama City, FL
        "index": "SPY",
        "sector_etfs": {
            "XLB": "Materials",
            "XLI": "Industrials",
            "XLP": "Consumer Staples",
            "KIE": "Insurance"
        },
        "regional_etfs": {
        "KRE": "Regional Banks"
        }
    },
    "louisiana_floods_2016": {
        "name": "Louisiana Floods",
        "type": "Flood",
        "event_date": "2016-08-12",
        "start_date": "2016-08-01",
        "end_date": "2016-08-31",
        "location": {"lat": 30.4515, "lon": -91.1871},  # Baton Rouge, LA
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLB": "Materials",
            "XLRE": "Real State",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    "kentucky_floods_2022": {
        "name": "Eastern Kentucky Floods",
        "type": "Flood",
        "event_date": "2022-07-28",
        "start_date": "2022-07-15",
        "end_date": "2022-08-15",
        "location": {"lat": 37.6456, "lon": -83.1141},  # Hazard, KY
        "index": "SPY",
        "sector_etfs": {
            "XLV": "Healthcare",
            "XLP": "Consumer Staples",
            "XLRE": "Real State",
            "KIE": "Insurance"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "helene_2024": {
        "name": "Hurricane Helene",
        "type": "Hurricane",
        "event_date": "2024-09-25",
        "start_date": "2024-09-20",
        "end_date": "2024-10-05",
        "location": {"lat": 35.2271, "lon": -80.8431},  # Charlotte, NC
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLI": "Industrials",
            "XLU": "Utilities",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "KIE": "Insurance",
            "IAK": "Insurance",
            "XTN": "Transportation",
            "KRE": "Regional Banks"
        }
    }
}


EVENT_FEATURES = {
    "Flood": [ 'temp', 'pressure', 'precip', 'humidity'],
    "Hurricane": ['temp', 'windspeed', 'pressure', 'precip', 'humidity'],
    "Wildfire": ['temp', 'windspeed', 'precip', 'humidity'],
    "WinterStorm": ['temp', 'windspeed', 'precip', 'humidity', 'solarradiation']
}

EVENT_COLOURS = {
    #"Drought" : 'orange',
    #"HeatWave" : 'darkred',
    "Flood" : 'green',
    "Hurricane" : 'purple',
    "Wildfire" : 'red',
    "WinterStorm" : 'blue'
}