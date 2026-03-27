#!/usr/bin/env python3
"""
Filter OpenFlights routes.dat to ALL direct international flights to Japan.

Data sources:
- routes.dat: https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat
- airports.dat: https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat

Usage:
    python3 filter_routes.py

Output: routes.json
"""

import json
import csv
import urllib.request
import os

ROUTES_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat"
AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
ROUTES_FILE = "/tmp/routes.dat"
AIRPORTS_FILE = "/tmp/airports.dat"

def download_if_needed(url, filepath):
    if not os.path.exists(filepath):
        print(f"Downloading {url}...")
        urllib.request.urlretrieve(url, filepath)

def main():
    download_if_needed(ROUTES_URL, ROUTES_FILE)
    download_if_needed(AIRPORTS_URL, AIRPORTS_FILE)

    airport_lookup = {}
    with open(AIRPORTS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 5 and row[4] and row[4] != '\\N':
                iata = row[4]
                airport_lookup[iata] = {
                    'city': row[2],
                    'name': row[1],
                    'country': row[3],
                }

    japanese_airports = {
        iata: data for iata, data in airport_lookup.items()
        if data['country'] == 'Japan'
    }
    print(f"Found {len(japanese_airports)} Japanese airports")

    AIRLINE_NAMES = {
        'NH': 'All Nippon Airways', 'JL': 'Japan Airlines', 'OZ': 'Asiana Airlines',
        'KE': 'Korean Air', 'CA': 'Air China', 'FM': 'Shanghai Airlines',
        'MU': 'China Eastern Airlines', 'CI': 'China Airlines', 'BR': 'EVA Air',
        'CX': 'Cathay Pacific', 'PR': 'Philippine Airlines', 'UA': 'United Airlines',
        'SU': 'Aeroflot', '5J': 'Cebu Pacific', 'ZH': 'Shenzhen Airlines',
        '3U': 'Sichuan Airlines', 'CZ': 'China Southern Airlines', 'HO': 'Juneyao Airlines',
        '9C': 'Spring Airlines', 'NX': 'Air Macau', 'DL': 'Delta Air Lines',
        'AA': 'American Airlines', '7C': 'Jeju Air', 'ZE': 'Eastar Jet',
        'TW': "T'way Air", 'LJ': 'Jin Air', 'BX': 'Air Busan',
        'RS': 'Air Seoul', 'JW': 'Vanilla Air', 'GK': 'Jetstar Japan',
        'BC': 'Skymark Airlines', 'MM': 'Peach Aviation',
        'TB': 'Tigerair Taiwan', 'IT': 'Tigerair Taiwan', 'GE': 'TransAsia Airways',
        'TZ': 'Scoot', 'TR': 'Scoot', '3K': 'Jetstar Asia', 'JQ': 'Jetstar',
        'QF': 'Qantas', 'EK': 'Emirates', 'EY': 'Etihad', 'QR': 'Qatar Airways',
        'SQ': 'Singapore Airlines', 'MH': 'Malaysia Airlines', 'TG': 'Thai Airways',
        'VN': 'Vietnam Airlines', 'S7': 'S7 Airlines', 'UO': 'HK Express',
        'HX': 'Hong Kong Airlines', 'PK': 'Pakistan International',
        'ET': 'Ethiopian Airlines', 'KQ': 'Kenya Airways', 'SA': 'South African Airways',
        'LA': 'LATAM', 'AC': 'Air Canada', 'AF': 'Air France', 'KL': 'KLM',
        'LH': 'Lufthansa', 'BA': 'British Airways', 'AZ': 'ITA Airways', 'IB': 'Iberia',
        'AY': 'Finnair', 'SK': 'SAS', 'OS': 'Austrian Airlines', 'SN': 'Brussels Airlines',
        'LO': 'LOT Polish', 'TK': 'Turkish Airlines', 'FJ': 'Fiji Airways',
        'HA': 'Hawaiian Airlines', 'AS': 'Alaska Airlines', 'TN': 'Air Tahiti Nui',
        'AE': 'Air France', 'KL': 'KLM', 'KX': 'Cayman Airways',
        'HF': 'Air Cote dIvoire', 'OS': 'Austrian', 'RO': 'TAROM',
        'VJ': 'Vietjet Air', 'QV': 'Lao Airlines', 'KA': 'Dragonair',
        'TR': 'Scoot', 'BI': 'Royal Brunei', 'GA': 'Garuda Indonesia',
        'PG': 'Bangkok Airways', 'FD': 'Thai AirAsia', 'AK': 'AirAsia',
        'D7': 'AirAsia X', 'XJ': 'Thai AirAsia X', 'Z2': 'Philippine AirAsia',
        'OD': 'Malindo Air', 'FY': 'Firefly', 'MH': 'Malaysia Airlines',
        'UL': 'SriLankan Airlines', 'W5': 'Mahan Air', 'IR': 'Iran Air',
        'RJ': 'Royal Jordanian', 'MS': 'EgyptAir', 'AT': 'Royal Air Maroc',
        'TK': 'Turkish Airlines', 'AZ': 'ITA Airways', 'JU': 'Air Serbia',
        'RO': 'TAROM', 'LO': 'LOT Polish', 'AY': 'Finnair', 'DY': 'Norwegian',
        'SK': 'SAS', 'KL': 'KLM', 'AF': 'Air France', 'LH': 'Lufthansa',
        'LX': 'SWISS', 'OS': 'Austrian', 'SN': 'Brussels Airlines', 'IB': 'Iberia',
        'TP': 'TAP Portugal', 'HV': 'Transavia', 'TO': 'Transavia France',
        'VY': 'Vueling', 'U2': 'easyJet', 'FR': 'Ryanair', 'W6': 'Wizz Air',
        'HU': 'Hainan Airlines', 'MF': 'Xiamen Airlines', '3U': 'Sichuan Airlines',
        'OQ': 'Chongqing Airlines', 'ZY': 'Shanghai Airlines', 'JD': 'Capital Airlines',
        'KN': 'China United', 'CZ': 'China Southern', 'MU': 'China Eastern',
    }

    routes_data = {}
    airlines_used = set()

    with open(ROUTES_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 9:
                continue

            airline = row[0]
            src_iata = row[2]
            _, _, _, _, dst_iata, _, _, stops_str, _ = row[:9]
            stops = int(stops_str) if stops_str else 0

            if dst_iata not in japanese_airports or stops != 0:
                continue
            if src_iata in japanese_airports:
                continue

            key = (src_iata, dst_iata)
            if key not in routes_data:
                src_info = airport_lookup.get(src_iata, {})
                routes_data[key] = {
                    'from': src_iata,
                    'fromCity': src_info.get('city', ''),
                    'fromCountry': src_info.get('country', ''),
                    'to': dst_iata,
                    'toCity': japanese_airports[dst_iata]['city'],
                    'toAirport': japanese_airports[dst_iata]['name'],
                    'direct': True,
                    'airlines': [],
                    'count': 0,
                }
            routes_data[key]['airlines'].append(airline)
            routes_data[key]['count'] += 1
            airlines_used.add(airline)

    routes = sorted(routes_data.values(), key=lambda r: (r['toCity'], r['from'], r['to']))
    airline_legend = {code: AIRLINE_NAMES.get(code, code) for code in airlines_used}

    output = {
        'source': 'OpenFlights Database',
        'license': 'https://openflights.org/data.html',
        'description': 'All direct international flights to Japan',
        'lastUpdated': '2026-03-26',
        'stats': {
            'totalRoutes': len(routes),
            'totalAirlines': len(airlines_used),
            'japaneseAirports': len(japanese_airports),
        },
        'airlines': airline_legend,
        'airports': japanese_airports,
        'routes': routes,
    }

    with open('routes.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nFound {len(routes)} direct international routes to Japan")
    print(f"Airlines: {len(airlines_used)}")

    print(f"\nTop 20 source airports:")
    source_counts = {}
    for r in routes:
        source_counts[r['from']] = source_counts.get(r['from'], 0) + 1
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1])[:20]:
        city = airport_lookup.get(src, {}).get('city', '?')
        print(f"  {src} ({city}): {count} routes")

    print(f"\nRoutes by Japanese destination:")
    dest_counts = {}
    for r in routes:
        dest_counts[r['to']] = dest_counts.get(r['to'], 0) + 1
    for dst, count in sorted(dest_counts.items(), key=lambda x: -x[1]):
        print(f"  {dst} ({japanese_airports[dst]['city']}): {count} routes")

if __name__ == '__main__':
    main()
