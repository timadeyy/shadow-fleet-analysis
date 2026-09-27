# Shadow Fleet Analysis

Analyzing AIS-based identity patterns (flag changes, name changes, unverified
vessel claims) for a sample of tankers linked to Russian sanctions evasion,
and estimating the value of the oil they can carry, using the Global Fishing
Watch API and public data from the KSE Institute.

## Status: Work in Progress 🟡

## Motivation
Following sanctions on Russian oil exports, a network of tankers with
opaque ownership and frequently changing flags/names — commonly called
the "shadow fleet" — has emerged to circumvent the price cap. This project
investigates whether identity-change patterns (flag hopping, name changes,
unverifiable AIS claims) can be detected and quantified from open data,
and how much oil value this sample of vessels can move per year.

## Data sources
- **[Global Fishing Watch API](https://globalfishingwatch.org/our-apis/)** — vessel identity history (flags, names, registry vs. self-reported data)
- **[KSE Institute](https://sanctions.kse.ua/)** — publicly reported list of sanctioned/unsanctioned shadow fleet tankers
- **[OpenSanctions – Ukraine War and Sanctions](https://www.opensanctions.org/datasets/ua_war_sanctions/)** — vessel specifications (deadweight, gross tonnage, build year), based on data from the Defence Intelligence of Ukraine (GUR); licensed under CC BY-NC 4.0, accessed 2026-09-25. *Planned: per-vessel DWT for the cargo estimate.*
- **Urals crude price** — 2025 annual average, used in the cargo value estimate

## Project structure
```
shadow-fleet-analysis/
├── data/
│   ├── shadow_fleet_vessels.csv      # Initial vessel list: IMO, name, size, owner and manager (KSE reports)
│   ├── shadow_FV.csv                 # TODO: what it contains; created in 01, used in ___
│   ├── identities.csv                # Full identity history from GFW: every flag/name ever linked to each IMO
│   ├── vessel_identities.csv         # Same as identities.csv, without the days_since_last_update column
│   ├── vessel_summary.csv            # One row per vessel: current verified identity + identity/flag counts
│   ├── flag_change_intervals.csv     # Flag before/after each change, with IMO
│   └── flag_df.csv                   # Flag before/after pairs, aggregated across the fleet
├── notebooks/
│   ├── 01_data_collection.ipynb      # Pulls vessel identity data from the GFW API, caches to CSV
│   ├── 02_flag_analysis.ipynb        # Flag-change frequency analysis, timeline construction
│   ├── 03_visualization.ipynb        # Flag changes before and after 2023
│   ├── 04_management_countries.ipynb # Registered owner vs ISM manager country, world map
│   ├── 05_cargo_value_estimate.ipynb # Cargo capacity ranges and estimated annual oil value by tanker class
│   └── utils.py                      # API request + JSON parsing functions
├── reports/
│   └── ism_map.png                   # World map: vessels managed per country (ISM manager)
└── README.md
```

## How to run
1. Create a `.env` file in the project root with `GFW_API_TOKEN=your_token`
2. Install dependencies into a virtual environment
3. Run the notebooks in order: `01 → 02 → 03 → 04 → 05`

## Key findings so far
- **Name mismatches**: the "currently verified" vessel name (per GFW registry)
  frequently does not match the name reported in KSE's sanctions tracking —
  likely because self-reported AIS name changes outpace official registry updates.
- **Panama is the most common flag** across the full identity history of the fleet.
- **IMO spoofing**: at least one IMO number in the sample was also self-reported
  by an unrelated vessel (a French navy vessel), suggesting AIS identity spoofing
  is present in the dataset.
- **Flag-change clustering**: preliminary case studies show vessels with long,
  stable identity periods (5+ years under one flag) followed by rapid flag-hopping
  (multiple changes within a single year) — investigating whether this clustering
  aligns with sanctions timeline events.
- **Tagor** is the most interesting vessel in the dataset. In **2012**, its AIS history
  shows an incident: for 8 days, a transmitter broadcast its IMO number under the name
  *"FRENCH NAVY WARSHIP"*. In **2026**, the tanker was **captured by the French Navy**
  in the Atlantic ([source](TODO: link to news article)).

## Cargo value estimate (notebook 05)
Estimated value of oil the 50 sampled tankers can carry per year:
**$TODO–TODO bn** (Urals 2025 average: $66.5/bbl).

**Method:**
DWT range by tanker class × voyages per year range × 0.95 load factor × 7.33 bbl/tonne × Urals price.
Results are given as a low–high range (scenario analysis) instead of a single number,
because vessel size and voyage frequency are uncertain.

| Tanker class | DWT range (t) | Voyages / year (assumed) |
|---|---|---|
| Handysize | 10,000 – 40,000 | 8 – 14 |
| Aframax | 80,000 – 110,000 | 5 – 8 |
| Suezmax | 120,000 – 200,000 | 4 – 7 |

**Assumptions & limitations:**
- DWT and voyages are class-based ranges, not per-vessel data
- Voyages per year are rough assumptions, to be replaced by a route-based calculation
- All cargo is treated as crude oil (7.33 bbl/t), although some vessels carry refined products
- A single annual average price is used; monthly price variation is ignored
- This is the **value of the cargo**, not the vessel operators' profit and not the amount
  that violates sanctions — only sales above the price cap are a violation

## Next steps
- [ ] Replace assumed voyages/year with a route-based estimate (sea distances) or GFW port-visit events
- [ ] Use per-vessel DWT from OpenSanctions instead of class-based ranges
- [ ] Use monthly Urals prices and the price-cap timeline to estimate the above-cap share
- [ ] Pull vessel-encounter (ship-to-ship transfer) events from GFW to add a behavioral layer
- [ ] Build summary visualizations (timeline chart, flag-change distribution, cargo value range by class)
