from datetime import datetime, timedelta
from skyfield.api import EarthSatellite, load
from geopy.distance import geodesic
import os
import math

SWATH_KM = {
    "aqua": [
        {"name": "MODIS", "swath_km": 2230, "type": "optical"},
        {"name": "AIRS", "swath_km": 1650, "type": "infrared"},
    ],
    "quickbird-2": [
        {"name": "Panchromatic", "swath_km": 16.5, "type": "optical"},
    ],
    "aura": [
        {"name": "OMI", "swath_km": 2600, "type": "optical"},
    ],
    "cbers-1": [     
        {"name": "WFI", "swath_km": 890, "type": "optical"},
        {"name": "CCD", "swath_km": 113, "type": "optical"},
        {"name": "IRMSS", "swath_km": 120, "type": "optical"}
    ],
    "envisat": [
        {"name": "MERIS", "swath_km": 1150},
        {"name": "ASAR", "swath_km": 405}
    ],
    "ers-1": [
        {"name": "AMI_SAR", "swath_km": 100, "type": "radar"},
        {"name": "ATSR-1", "swath_km": 500, "type": "optical"}
    ],
    "ers-2": [
        {"name": "AMI_SAR", "swath_km": 100, "type": "radar"},
        {"name": "ATSR-2", "swath_km": 500, "type": "optical"}
    ],        
    "goes-4": [
        {"name": "GOES", "swath_km": 1665, "type": "optical"}
    ],
    "goes-5": [
        {"name": "GOES", "swath_km": 1665, "type": "optical"}
    ],
    "goes-6": [
        {"name": "GOES", "swath_km": 1665, "type": "optical"}
    ],
    "goes-7": [
        {"name": "GOES", "swath_km": 1665, "type": "optical"}
    ],
    "goes-8": [
        {"name": "GOES", "swath_km": 8150, "type": "optical"}
    ],
    "goes-9": [
        {"name": "GOES", "swath_km": 8150, "type": "optical"}
    ],
    "goes-10": [
        {"name": "GOES", "swath_km": 8150, "type": "optical"}
    ],
    "goes-11": [
        {"name": "GOES", "swath_km": 8150, "type": "optical"}
    ],
    "goes-12": [
        {"name": "GOES", "swath_km": 8150, "type": "optical"}
    ],
    "jers-1": [
        {"name": "SAR", "swath_km": 175, "type": "radar"},
        {"name": "OPS", "swath_km": 75, "type": "optical"}
    ],    
    "landsat4": [
        {"name": "TM", "swath_km": 185, "type": "optical"},
        {"name": "MSS", "swath_km": 185, "type": "optical"}
    ],
    "landsat5": [
        {"name": "TM", "swath_km": 185, "type": "optical"},
        {"name": "MSS", "swath_km": 185, "type": "optical"}
    ],    
    "landsat7": [
        {"name": "ETM+", "swath_km": 183, "type": "optical"}
    ],
    "noaa-6": [
        {"name": "AVHRR/1", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-07": [
        {"name": "AVHRR/2", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-08": [
        {"name": "AVHRR/1", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-09": [
        {"name": "AVHRR/2", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-10": [
        {"name": "AVHRR/1", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-11": [
        {"name": "AVHRR/2", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-12": [
        {"name": "AVHRR/2", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-13": [
        {"name": "AVHRR/2", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-14": [
        {"name": "AVHRR/2", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-15": [
        {"name": "AVHRR/3", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-16": [
        {"name": "AVHRR/3", "swath_km": 2900, "type": "optical"}
    ],
    "noaa-17": [
        {"name": "AVHRR/3", "swath_km": 2900, "type": "optical"}
    ],
    "spot-1": [
        {"name": "HRV", "swath_km": 60, "type": "optical"}
    ],
    "spot-2": [
        {"name": "HRV", "swath_km": 60, "type": "optical"}
    ],
    "spot-3": [
        {"name": "HRV", "swath_km": 60, "type": "optical"}
    ],
    "spot-4": [
        {"name": "HRVIR", "swath_km": 60, "type": "optical"},
        {"name": "vegetation", "swath_km": 2200, "type": "optical"}
    ],
    "spot-5": [
        {"name": "HRG", "swath_km": 60, "type": "optical"},
        {"name": "HRS", "swath_km": 120, "type": "optical"},
        {"name": "vegetation", "swath_km": 2200, "type": "optical"}
    ],
    "terra": [
        {"name": "MODIS", "swath_km": 2230, "type": "optical"},
        {"name": "ASTER", "swath_km": 60, "type": "optical"},
        {"name": "MOPITT", "swath_km": 640, "type": "infrared"},
        {"name": "MISR", "swath_km": 380, "type": "optical"}
    ],
    "trmm": [
        {"name": "PR", "swath_km": 2230, "type": "radar"},
        {"name": "TMI", "swath_km": 60, "type": "microwave"},
        {"name": "VIRS", "swath_km": 640, "type": "optical"},
        {"name": "LIS", "swath_km": 380, "type": "optical"}
    ]
}

# Load TLEs from a folder
def load_tle_from_folder(folder_path):
    tle_dict = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            path = os.path.join(folder_path, filename)
            with open(path, 'r') as f:
                lines = f.readlines()
                for i in range(len(lines) - 1):
                    if lines[i].startswith('1 ') and lines[i + 1].startswith('2 '):
                        name = filename.replace('.txt', '')
                        tle_dict[name] = (lines[i].strip(), lines[i + 1].strip())
                        break
    return tle_dict

# Main function: check if satellite covers point at specific time
def find_satellites_near(folder_path, target_lat, target_lon, time_utc):
    tles = load_tle_from_folder(folder_path)
    matching_sats = []
    ts = load.timescale()

    for name, (tle1, tle2) in tles.items():
        try:
            t = ts.utc(time_utc.year, time_utc.month, time_utc.day,
                       time_utc.hour, time_utc.minute, time_utc.second)
            sat = EarthSatellite(tle1, tle2, name, ts)
            geo = sat.at(t)
            sub = geo.subpoint()
            sat_lat, sat_lon = sub.latitude.degrees, sub.longitude.degrees
            elevation_km = sub.elevation.km

            swath_km = None
            if name.lower() in SWATH_KM:
                instruments = SWATH_KM[name.lower()]
                for inst in instruments:
                    if inst["type"] in ["optical", "radar", "infrared", "microwave"]:
                        swath_km = inst["swath_km"]
                        break

            if not swath_km:
                continue

            dist = geodesic((target_lat, target_lon), (sat_lat, sat_lon)).km
            print(f"Checking {name} at {time_utc}, dist = {dist:.1f}, swath = {swath_km}")


            if dist <= swath_km / 2:
                matching_sats.append((name, time_utc, dist, swath_km, (sat_lat, sat_lon), elevation_km))
        except Exception:
            continue
    return matching_sats

# Function to scan a time range and return all satellite passes
def find_satellites_in_time_range(folder_path, target_lat, target_lon, time_start, time_end, step_minutes=10):
    sats_found = []
    time = time_start
    while time <= time_end:
        sats = find_satellites_near(folder_path, target_lat, target_lon, time)
        sats_found.extend(sats)
        time += timedelta(minutes=step_minutes)
    return sats_found

# Run example
if __name__ == "__main__":
    folder_path = "C:/Users/talsh/Desktop/Noam/SHIMRIT/UN-SPIDER/TLE" 
    target_lat = 6.585389
    target_lon = 79.960750
    time_start = datetime(2004, 12, 26, 2, 0, 0)
    time_end   = datetime(2004, 12, 26, 8, 0, 0)

    results = find_satellites_in_time_range(folder_path, target_lat, target_lon, time_start, time_end)

    for name, time, dist, swath_km, (lat, lon), elev in results:
        print(f"- {name} at {time}:")
        print(f"    Distance to target = {dist:.1f} km")
        print(f"    Swath width        = {swath_km:.0f} km")
        print(f"    Subsatellite point = ({lat:.2f}, {lon:.2f})")
        print(f"    Elevation          = {elev:.1f} km\n")