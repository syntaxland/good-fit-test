"""
Qlay Good Fit Test — Driver Profile Extraction & Load Matching
Author: JonDeBosco
"""

import math
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# 1. HAVERSINE DISTANCE
# ---------------------------------------------------------------------------

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return straight-line distance in miles between two lat/lon points."""
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# 2. DRIVER PROFILE  (extracted from Sample Conversation)
# ---------------------------------------------------------------------------

@dataclass
class DriverProfile:
    current_location: str
    current_lat: float
    current_lon: float
    home_base: str
    home_lat: float
    home_lon: float
    min_rate_per_mile: float       # $/mile
    equipment_types: list          # e.g. ['Hotshot', 'Flatbed', 'Gooseneck']
    weight_capacity_lb: int


# Evidence from conversation:
#   "I'm in Dallas"                         -> current location
#   "you're based out in San Antonio"       -> home base (dispatch confirms)
#   "above $2 per mile"                     -> minimum rate
#   asks about "hotshots, flatbeds, goosenecks" and dispatch confirms all three
#   asks about a 44,000 lb load without objecting -> weight capacity

DRIVER = DriverProfile(
    current_location="Dallas, TX",
    current_lat=32.7767,
    current_lon=-96.7970,
    home_base="San Antonio, TX",
    home_lat=29.4241,
    home_lon=-98.4936,
    min_rate_per_mile=2.00,
    equipment_types=["Hotshot", "Flatbed", "Gooseneck"],
    weight_capacity_lb=44_000,
)


# ---------------------------------------------------------------------------
# 3. LOAD DATA
# ---------------------------------------------------------------------------

@dataclass
class Load:
    load_id: str
    origin: str
    origin_lat: float
    origin_lon: float
    destination: Optional[str]
    dest_lat: Optional[float]
    dest_lon: Optional[float]
    trailer: str
    weight_lb: int
    price: Optional[float]


LOADS = [
    Load("L01", "Fort Worth",  32.7555, -97.3308, "Oklahoma City",  35.4676, -97.5164, "Van",      42000,  620.0),
    Load("L02", "Houston",     29.7604, -95.3698, "Laredo",         27.5306, -99.4803, "Hotshot",  11500, 1600.0),
    Load("L03", "Austin",      30.2672, -97.7431, "Corpus Christi", 27.8006, -97.3964, "Gooseneck",14200, 1500.0),
    Load("L04", "Plano",       33.0198, -96.6989, "Memphis",        35.1495, -90.0490, "Van",      38000, 1500.0),
    Load("L05", "Waco",        31.5493, -97.1467, "San Antonio",    29.4241, -98.4936, "Flatbed",   9800,  640.0),
    Load("L06", "Shreveport",  32.5252, -93.7502, "Atlanta",        33.7490, -84.3880, "Van",      46500,  None),
    Load("L07", "Tulsa",       36.1540, -95.9928,  None,             None,    None,    "Hotshot",  13400, 1100.0),
    Load("L08", "Dallas",      32.7767, -96.7970, "McAllen",        26.2034, -98.2300, "Hotshot",  12600, 1700.0),
]


# ---------------------------------------------------------------------------
# 4. ELIGIBILITY FILTER
# ---------------------------------------------------------------------------

def check_eligibility(load: Load, driver: DriverProfile) -> tuple[bool, list[str]]:
    """Return (is_eligible, list_of_reasons_if_not)."""
    reasons = []

    if load.trailer not in driver.equipment_types:
        reasons.append(f"trailer '{load.trailer}' not in driver equipment {driver.equipment_types}")

    if load.weight_lb > driver.weight_capacity_lb:
        reasons.append(f"weight {load.weight_lb:,} lb exceeds capacity {driver.weight_capacity_lb:,} lb")

    if load.price is None:
        reasons.append("price is MISSING — cannot compute rate")

    if load.destination is None or load.dest_lat is None:
        reasons.append("destination is MISSING — cannot compute loaded miles")

    return (len(reasons) == 0, reasons)


# ---------------------------------------------------------------------------
# 5. EFFECTIVE RATE CALCULATION
# ---------------------------------------------------------------------------

def effective_rate(load: Load, driver: DriverProfile) -> dict:
    """
    effective_rate/mile = price / (deadhead_to_origin + loaded_miles)

    deadhead_to_origin = driver's current location -> load origin (haversine)
    loaded_miles       = load origin -> destination (haversine)
    """
    deadhead = haversine(
        driver.current_lat, driver.current_lon,
        load.origin_lat,   load.origin_lon,
    )
    loaded = haversine(
        load.origin_lat, load.origin_lon,
        load.dest_lat,   load.dest_lon,
    )
    total = deadhead + loaded
    rate  = load.price / total
    return {
        "load_id":      load.load_id,
        "origin":       load.origin,
        "destination":  load.destination,
        "trailer":      load.trailer,
        "weight_lb":    load.weight_lb,
        "price":        load.price,
        "deadhead_mi":  round(deadhead, 2),
        "loaded_mi":    round(loaded,   2),
        "total_mi":     round(total,    2),
        "rate_per_mi":  round(rate,     3),
    }


# ---------------------------------------------------------------------------
# 6. MAIN — filter, rank, report
# ---------------------------------------------------------------------------

def main():
    print("=" * 65)
    print("PART A — DRIVER PROFILE")
    print("=" * 65)
    print(f"  Current Location  : {DRIVER.current_location}")
    print(f"  Current Lat/Lon   : {DRIVER.current_lat}, {DRIVER.current_lon}")
    print(f"  Home Base         : {DRIVER.home_base}")
    print(f"  Home Lat/Lon      : {DRIVER.home_lat}, {DRIVER.home_lon}")
    print(f"  Min Rate/Mile     : ${DRIVER.min_rate_per_mile:.2f}")
    print(f"  Equipment         : {', '.join(DRIVER.equipment_types)}")
    print(f"  Weight Capacity   : {DRIVER.weight_capacity_lb:,} lb")

    print("\n" + "=" * 65)
    print("PART B — ELIGIBILITY FILTER")
    print("=" * 65)

    eligible_results = []
    ineligible_results = []

    for load in LOADS:
        is_eligible, reasons = check_eligibility(load, DRIVER)
        if is_eligible:
            result = effective_rate(load, DRIVER)
            eligible_results.append(result)
            print(f"  {load.load_id}: ELIGIBLE")
        else:
            ineligible_results.append((load.load_id, reasons))
            for r in reasons:
                print(f"  {load.load_id}: INELIGIBLE — {r}")

    # Sort by effective rate descending
    eligible_results.sort(key=lambda x: x["rate_per_mi"], reverse=True)

    print("\n" + "=" * 65)
    print("PART B — TOP 3 LOADS (ranked by effective rate/mile)")
    print("=" * 65)
    for rank, r in enumerate(eligible_results[:3], 1):
        print(f"\n  Rank {rank}: {r['load_id']}  |  {r['origin']} → {r['destination']}")
        print(f"    Trailer       : {r['trailer']}")
        print(f"    Weight        : {r['weight_lb']:,} lb")
        print(f"    Price         : ${r['price']:,.0f}")
        print(f"    Deadhead      : {r['deadhead_mi']} mi")
        print(f"    Loaded miles  : {r['loaded_mi']} mi")
        print(f"    Total miles   : {r['total_mi']} mi")
        print(f"    Eff. Rate     : ${r['rate_per_mi']:.3f}/mi")

    if len(eligible_results) > 3:
        print(f"\n  (Rank 4 — not in top 3: {eligible_results[3]['load_id']} "
              f"@ ${eligible_results[3]['rate_per_mi']:.3f}/mi)")


if __name__ == "__main__":
    main()