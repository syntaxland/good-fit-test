# Qlay Good Fit Test — Driver Profile Extraction & Load Matching

## How to Run

```bash
python3 solution.py
```

No dependencies beyond the Python standard library.

---

## Part A — Extraction Assumptions

Profile fields were inferred from dispatcher/driver dialogue, not stated explicitly:

| Field | Evidence from conversation |
|---|---|
| Current location | Driver says *"I'm in Dallas"* |
| Home base | Dispatcher confirms *"you're based out in San Antonio"* |
| Min rate/mile | Driver says *"above $2 per mile"* → set to $2.00 |
| Equipment | Driver asks about *"hotshots, flatbeds, goosenecks"*; dispatcher confirms all three |
| Weight capacity | Driver asks about a 44,000 lb load without objecting → 44,000 lb |

---

## Part B — Ranking Logic

```
effective_rate = price ÷ (deadhead_to_origin + loaded_miles)
```

All distances are straight-line haversine from provided lat/lon coordinates.  
Driver's current location (Dallas) is used as deadhead origin.

**Ineligible loads excluded before ranking:**

| Load | Reason |
|---|---|
| L01, L04 | Van trailer — driver does not run Vans |
| L06 | Van trailer + overweight (46,500 lb > 44,000 lb) + price MISSING |
| L07 | Destination MISSING — loaded miles incalculable |

**Top 3 results:** L03 ($4.239/mi) → L08 ($3.678/mi) → L02 ($3.090/mi)

---

## Sample Output

```
=================================================================
PART A — DRIVER PROFILE
=================================================================
  Current Location  : Dallas, TX
  Current Lat/Lon   : 32.7767, -96.797
  Home Base         : San Antonio, TX
  Home Lat/Lon      : 29.4241, -98.4936
  Min Rate/Mile     : $2.00
  Equipment         : Hotshot, Flatbed, Gooseneck
  Weight Capacity   : 44,000 lb

=================================================================
PART B — ELIGIBILITY FILTER
=================================================================
  L01: INELIGIBLE — trailer 'Van' not in driver equipment ['Hotshot', 'Flatbed', 'Gooseneck']
  L02: ELIGIBLE
  L03: ELIGIBLE
  L04: INELIGIBLE — trailer 'Van' not in driver equipment ['Hotshot', 'Flatbed', 'Gooseneck']
  L05: ELIGIBLE
  L06: INELIGIBLE — trailer 'Van' not in driver equipment ['Hotshot', 'Flatbed', 'Gooseneck']
  L06: INELIGIBLE — weight 46,500 lb exceeds capacity 44,000 lb
  L06: INELIGIBLE — price is MISSING — cannot compute rate
  L07: INELIGIBLE — destination is MISSING — cannot compute loaded miles
  L08: ELIGIBLE

=================================================================
PART B — TOP 3 LOADS (ranked by effective rate/mile)
=================================================================

  Rank 1: L03  |  Austin → Corpus Christi
    Trailer       : Gooseneck
    Weight        : 14,200 lb
    Price         : $1,500
    Deadhead      : 182.12 mi
    Loaded miles  : 171.71 mi
    Total miles   : 353.83 mi
    Eff. Rate     : $4.239/mi

  Rank 2: L08  |  Dallas → McAllen
    Trailer       : Hotshot
    Weight        : 12,600 lb
    Price         : $1,700
    Deadhead      : 0.0 mi
    Loaded miles  : 462.26 mi
    Total miles   : 462.26 mi
    Eff. Rate     : $3.678/mi

  Rank 3: L02  |  Houston → Laredo
    Trailer       : Hotshot
    Weight        : 11,500 lb
    Price         : $1,600
    Deadhead      : 224.8 mi
    Loaded miles  : 292.99 mi
    Total miles   : 517.79 mi
    Eff. Rate     : $3.090/mi

  (Rank 4 — not in top 3: L05 @ $2.514/mi)
```