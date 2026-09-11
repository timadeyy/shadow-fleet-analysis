import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("GFW_API_TOKEN")
headers = {"Authorization": f"Bearer {token}"}

def get_vessel_info(imo):
    url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search"
    params = {
        "query": imo,
        "datasets[0]": "public-global-vessel-identity:latest"
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Error for imo {imo}: status code {response.status_code}")
        return None
    return response.json()

def parse_vessel_data(imo, raw_data):
    if raw_data is None or raw_data['total'] == 0:
        return {"imo": imo, "found": False}, []

    all_identities = []
    for entry in raw_data['entries']:
        source_records = (
            entry['registryInfo']
            if entry['registryInfo']
            else entry['selfReportedInfo']
        )
        for record in source_records:
            all_identities.append({
                "imo": imo,
                "shipname": record.get('shipname'),
                "flag": record.get('flag'),
                "ssvid": record.get('ssvid'),
                "match_fields": record.get('matchFields', 'REGISTRY'),
                "transmission_from": record.get('transmissionDateFrom'),
                "transmission_to": record.get('transmissionDateTo'),
                "is_verified": record.get('matchFields') == 'SEVERAL_FIELDS' or 'sourceCode' in record and record.get('sourceCode') == ['IMO'],
            })

    verified = [r for r in all_identities if r['is_verified']]
    current = max(verified, key=lambda r: r['transmission_to'] or '') if verified else all_identities[0]

    summary = {
        "imo": imo,
        "found": True,
        "current_name": current['shipname'],
        "current_flag": current['flag'],
        "num_total_identities": len(all_identities),
        "num_verified_identities": len(verified),
        "num_suspicious_matches": len(all_identities) - len(verified),
    }
    return summary, all_identities