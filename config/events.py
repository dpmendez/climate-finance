# Number of trading days before the event used to estimate the CAPM market model.
# 120 trading days (~6 months) is standard in event-study literature.
ESTIMATION_DAYS = 120

# Default number of calendar days before the event to include in the analysis window.
# Controls how many negative relative_day observations enter the pooled dataset.
EVENT_TYPE_DEFAULTS = {
    "Hurricane":    {"pre_event_days": 14},
    "Wildfire":     {"pre_event_days": 7},
    "Flood":        {"pre_event_days": 7},
    "WinterStorm":  {"pre_event_days": 14},
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

# Declare dictionary of events
# Each event is a dictionary with metadata
EVENTS = {
    # Hurricanes
    "harvey_2017": {
        "name": "Hurricane Harvey",
        "type": "Hurricane",
        "event_date": "2017-08-25",
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
    "michael_2018": {
        "name": "Hurricane Michael",
        "type": "Hurricane",
        "event_date": "2018-10-10",
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
    "ida_2021": {
        "name": "Hurricane Ida",
        "type": "Hurricane",
        "event_date": "2021-08-29",
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
    "helene_2024": {
        "name": "Hurricane Helene",
        "type": "Hurricane",
        "event_date": "2024-09-25",
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
    },
    "milton_2024": {
        "name": "Hurricane Milton",
        "type": "Hurricane",
        "event_date": "2024-10-09",
        "end_date": "2024-10-12",
        "location": {"lat": 27.3, "lon": -82.6},  # Siesta Key / Tampa Bay area
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "XLI": "Industrials",
            "XLP": "Consumer Staples",
            "XLU": "Utilities"
        },
        "regional_etfs": {
            "XLRE": "Real Estate", # Regional exposure
            "IAT": "Regional Banks" # Regional Banks ETF (many FL banks)
        }
    },
    "sandy_2012": {
        "name": "Hurricane Sandy",
        "type": "Hurricane",
        "event_date": "2012-10-29",
        "end_date": "2012-11-15",
        "location": {"lat": 40.7128, "lon": -74.0060},  # New York City, NY
        "index": "SPY",
        "sector_etfs": {
            "XLF": "Financials",
            "KIE": "Insurance",
            "XLU": "Utilities",
            "XLRE": "Real Estate",
            "IYT": "Transports",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "matthew_2016": {
        "name": "Hurricane Matthew",
        "type": "Hurricane",
        "event_date": "2016-10-08",
        "end_date": "2016-10-22",
        "location": {"lat": 34.0007, "lon": -79.9766},  # Florence, SC
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLB": "Materials",
            "XLRE": "Real Estate",
            "XLF": "Financials"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "nate_2017": {
        "name": "Hurricane Nate",
        "type": "Hurricane",
        "event_date": "2017-10-07",
        "end_date": "2017-10-20",
        "location": {"lat": 30.3960, "lon": -88.8853},  # Biloxi, MS
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLE": "Energy",
            "XLP": "Consumer Staples",
            "XLY": "Consumer Discretionary",
            "IYT": "Transports"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "florence_2018": {
        "name": "Hurricane Florence",
        "type": "Hurricane",
        "event_date": "2018-09-14",
        "end_date": "2018-10-01",
        "location": {"lat": 34.2104, "lon": -77.8868},  # Wilmington, NC
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLB": "Materials",
            "XLRE": "Real Estate",
            "XLI": "Industrials"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "dorian_2019": {
        "name": "Hurricane Dorian",
        "type": "Hurricane",
        "event_date": "2019-09-06",
        "end_date": "2019-09-20",
        "location": {"lat": 35.2335, "lon": -75.6209},  # Cape Hatteras, NC
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLRE": "Real Estate",
            "JETS": "Airlines",
            "XLY": "Consumer Discretionary"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "laura_2020": {
        "name": "Hurricane Laura",
        "type": "Hurricane",
        "event_date": "2020-08-27",
        "end_date": "2020-09-10",
        "location": {"lat": 30.2266, "lon": -93.2174},  # Lake Charles, LA
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLI": "Industrials",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLB": "Materials"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    "delta_2020": {
        "name": "Hurricane Delta",
        "type": "Hurricane",
        "event_date": "2020-10-09",
        "end_date": "2020-10-23",
        "location": {"lat": 30.2266, "lon": -93.2174},  # Lake Charles, LA
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLB": "Materials"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    "zeta_2020": {
        "name": "Hurricane Zeta",
        "type": "Hurricane",
        "event_date": "2020-10-28",
        "end_date": "2020-11-10",
        "location": {"lat": 29.9511, "lon": -90.0715},  # New Orleans, LA
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "KIE": "Insurance",
            "XLU": "Utilities",
            "XLP": "Consumer Staples",
            "XLI": "Industrials"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    "ian_2022": {
        "name": "Hurricane Ian",
        "type": "Hurricane",
        "event_date": "2022-09-28",
        "end_date": "2022-10-15",
        "location": {"lat": 26.6406, "lon": -81.8723},  # Fort Myers, FL
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLF": "Financials",
            "XLU": "Utilities",
            "XLRE": "Real Estate",
            "XLP": "Consumer Staples",
            "XLB": "Materials",
            "XLI": "Industrials"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "nicole_2022": {
        "name": "Hurricane Nicole",
        "type": "Hurricane",
        "event_date": "2022-11-10",
        "end_date": "2022-11-20",
        "location": {"lat": 27.6386, "lon": -80.3931},  # Vero Beach, FL
        "index": "SPY",
        "sector_etfs": {
            "KIE": "Insurance",
            "XLRE": "Real Estate",
            "XLU": "Utilities",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "KRE": "Regional Banks"
        }
    },
    "beryl_2024": {
        "name": "Hurricane Beryl",
        "type": "Hurricane",
        "event_date": "2024-07-08",
        "end_date": "2024-07-22",
        "location": {"lat": 29.7604, "lon": -95.3698},  # Houston, TX
        "index": "SPY",
        "sector_etfs": {
            "XLE": "Energy",
            "XLU": "Utilities",
            "KIE": "Insurance",
            "XLP": "Consumer Staples",
            "XLF": "Financials"
        },
        "regional_etfs": {
            "SMEZ": "Midcap Energy",
            "KRE": "Regional Banks"
        }
    },
    
    # Wildfires
    "wildfires_west_2020": {
        "name": "Western U.S. Wildfires 2020",
        "type": "Wildfire",
        "event_date": "2020-09-01",
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
    "maui_2023": {
        "name": "Maui Wildfires 2023",
        "type": "Wildfire",
        "event_date": "2023-08-08",
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
    "wildfires_southcal_2025": {
        "name": "Southern California Wildfires 2025",
        "type": "Wildfire",
        "event_date": "2025-01-15",
        "end_date": "2025-01-31",
        "location": {"lat": 34.05, "lon": -118.25},  # Los Angeles
        "index": "SPY",
        "sector_etfs": {
            "XLU": "Utilities",
            "XLE": "Energy",
            "XLI": "Industrials",
            "XLRE": "Real Estate"
        },
        "regional_etfs": {
            "PWZ": "California AMT-Free Municipal Bonds", # Invesco California AMT-Free Municipal Bond ETF
            "CMF": "iShares California Muni Bonds" # iShares California Muni Bond ETF
        }
    },
    "madrefire_2025": {
        "name": "Madre Fire 2025",
        "type": "Wildfire",
        "event_date": "2025-07-31",
        "end_date": "2025-08-05",
        "location": {"lat": 34.5, "lon": -120.0},  # Likely coastal California region
        "index": "SPY",
        "sector_etfs": {
            "XLU": "Utilities",
            "XLE": "Energy",
            "XLRE": "Real Estate",
            "XLV": "Healthcare"
        },
        "regional_etfs": {
            "WOOD": "Timber & Forestry exposure",
            "KIE": "Insurance sector exposure",
            "ITB": "Home Construction exposure"
        }
    },

    # Winter Storms
    "winter_storm_uri_2021": {
        "name": "Winter Storm Uri",
        "type": "WinterStorm",
        "event_date": "2021-02-15",
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

    # Floods
    "louisiana_floods_2016": {
        "name": "Louisiana Floods 2016",
        "type": "Flood",
        "event_date": "2016-08-12",
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
        "name": "Kentucky Floods 2022",
        "type": "Flood",
        "event_date": "2022-07-28",
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
    "centraltexas_floods_2025": {
        "name": "Central Texas Floods 2025",
        "type": "Flood",
        "event_date": "2025-07-04",
        "end_date": "2025-07-07",
        "location": {"lat": 30.1, "lon": -99.1},  # Kerr County / Hill Country
        "index": "SPY",
        "sector_etfs": {
            "XLF": "Financials",
            "XLRE": "Real Estate",
            "XLI": "Industrials",
            "XLP": "Consumer Staples"
        },
        "regional_etfs": {
            "TEXN": "iShares Texas Equity ETF", # Tracks major Texas-headquartered firms like Oracle and Tesla
            "TXS": "Texas Equity Index ETF" # Diversified exposure to Texas economy, energy, and infrastructure
        }
    }
}