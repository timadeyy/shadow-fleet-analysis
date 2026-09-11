import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GFW_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}


def get_vessel_info(imo):
  url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search"
  params = {"query": imo, "datasets[0]": "public-global-vessel-identity:latest"}
  try:
    response = requests.get(url, headers=headers, params=params, timeout=15)
    if response.status_code != 200:
      print(f"Error for imo {imo}: status code {response.status_code}")
      return None
    return response.json()
  except requests.RequestException as e:
    print(f"Network error for imo {imo}: {e}")
    return None


def parse_vessel_data(imo, raw_data):
  if not raw_data or raw_data.get("total", 0) == 0:
    return {"imo": imo, "found": False}, []

  all_identities = []
  for entry in raw_data.get("entries", []):
    for record in entry.get("registryInfo", []):
      is_imo_source = (
          "sourceCode" in record and "IMO" in record.get("sourceCode", [])
      )
      all_identities.append({
          "imo": imo,
          "source": "registry",
          "shipname": record.get("shipname"),
          "flag": record.get("flag"),
          "ssvid": record.get("ssvid"),
          "match_fields": record.get("matchFields", "REGISTRY"),
          "transmission_from": record.get("recordDateFrom")
          or record.get("transmissionDateFrom"),
          "transmission_to": record.get("recordDateTo")
          or record.get("transmissionDateTo"),
          "is_verified": is_imo_source
          or record.get("matchFields") == "SEVERAL_FIELDS",
      })

    # 2. Actual AIS messages
    for record in entry.get("selfReportedInfo", []):
      all_identities.append({
          "imo": imo,
          "source": "self_reported",
          "shipname": record.get("shipname"),
          "flag": record.get("flag"),
          "ssvid": record.get("ssvid"),
          "match_fields": record.get("matchFields", "NO_MATCH"),
          "transmission_from": record.get("transmissionDateFrom"),
          "transmission_to": record.get("transmissionDateTo"),
          "is_verified": record.get("matchFields") == "SEVERAL_FIELDS",
      })

  if not all_identities:
    return {"imo": imo, "found": False}, []

  # Determine the current profile based on the most recent activity date
  dated = [r for r in all_identities if r.get("transmission_to")]
  current = (
      max(dated, key=lambda r: str(r["transmission_to"]))
      if dated
      else all_identities[0]
  )

  registry_count = sum(1 for r in all_identities if r["source"] == "registry")
  self_rep_count = sum(
      1 for r in all_identities if r["source"] == "self_reported"
  )
  verified_count = sum(1 for r in all_identities if r["is_verified"])

  # Unique Flags According to Official Data vs. According to AIS
  reg_flags = {
      r["flag"] for r in all_identities if r["source"] == "registry" and r["flag"]
  }
  ais_flags = {
      r["flag"]
      for r in all_identities
      if r["source"] == "self_reported" and r["flag"]
  }

  summary = {
      "imo": imo,
      "found": True,
      "current_name": current.get("shipname"),
      "current_flag": current.get("flag"),
      "num_total_identities": len(all_identities),
      "num_registry_records": registry_count,
      "num_self_reported": self_rep_count,
      "num_verified_identities": verified_count,
      "num_unique_flags": len(reg_flags | ais_flags),
      "has_flag_discrepancy": bool(
          ais_flags - reg_flags
      ),  # transmitted a flag to the AIS that is not listed in the registry
  }

  return summary, all_identities