# Shadow Fleet Analysis

Analyzing AIS-based identity patterns (flag changes, name changes, unverified 
vessel claims) for a sample of tankers linked to Russian sanctions evasion, 
using the Global Fishing Watch API and public data from the KSE Institute.

## Status: Work in Progress 🟡

## Motivation
Following sanctions on Russian oil exports, a network of tankers with 
opaque ownership and frequently changing flags/names — commonly called 
the "shadow fleet" — has emerged to circumvent the price cap. This project 
investigates whether identity-change patterns (flag hopping, name changes, 
unverifiable AIS claims) can be detected and quantified from open data.

## Data sources
- **[Global Fishing Watch API](https://globalfishingwatch.org/our-apis/)** — vessel identity history (flags, names, registry vs. self-reported data)
- **[KSE Institute](https://sanctions.kse.ua/)** — publicly reported list of sanctioned/unsanctioned shadow fleet tankers

## Project structure
```
shadow-fleet-analysis/
├── data/
│   ├── shadow_fleet_vessels.csv      # Initial vessel list (IMO, name, owner info from KSE reports)
│   ├── vessel_summary.csv            # One row per vessel: current verified identity + suspicious match count
│   └── vessel_identities.csv         # Full identity history: every flag/name ever linked to each IMO
├── notebooks/
│   ├── 01_data_collection.ipynb      # Pulls vessel identity data from GFW API, caches to CSV
│   ├── 02_flag_analysis.ipynb        # Flag-change frequency analysis, timeline construction
│   └── utils.py                      # API request + JSON parsing functions
└── README.md
```

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
in the Atlantic.

## Next steps
- [ ] Pull port-visit and vessel-encounter event data from GFW to add a behavioral layer
- [ ] Build summary visualizations (timeline chart, flag-change distribution)}
