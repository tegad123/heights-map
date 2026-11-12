"""Per-market config for the multi-market permit pipeline (2026-08-27).

Consumed by weekly_ingest_driver.py, which overrides permit_pull's
market-scoped globals (BOUNDARY_GEOJSON + ring reload, COORD_BOX,
PERMITS_JSON_NAME, LNG_EAST_MAX) per market. permit_pull.py's defaults
ARE the heights entry — a bare `import permit_pull` stays Heights-correct.

Field notes:
- zips: evidence-based from each market's permits JSON + DATA (audit 2026-08-27).
  Overlaps are real and intended: 77019 (montrose+riveroaks), 77008
  (heights+timbergrove) — boundary polygons disambiguate, and the driver
  suppresses OOZ-POLY quarantine for rows that fall inside another
  enabled market's ring.
- boundary: geojson in repo root. montrose/riveroaks/springbranch/timbergrove
  extracted from each page's HD_POLYS ring; gardenoaksoakforest is the union
  of garden_oaks/*_boundary_filled.geojson (commercial-frontage overreach on
  N Shepherd / W 43rd is mitigated by the S.F. RES filter — eyeball those
  frontages in dry-runs, CLAUDE.md known issue). westu has NO polygon:
  its HD_POLYS is the strict city boundary but the market is all of 77005
  (Southampton/Rice Village pins included since the 07-08 build), so the
  zone guard is zip + coord box only.
- coord_box: (lat_min, lat_max, lng_min, lng_max), boundary bbox +-0.01 deg.
- east_lng: Heights-only I-45 corridor cutoff. None elsewhere.
- springvalley stays out of permit ingest (enabled False, not in
  INGEST_ORDER) until springvalley_permits.json exists. HAR sold/active
  refresh does include it. The boundary is the Census incorporated-place
  limit, GEOID 4869830, not the whole 77024 ZIP. See
  springvalley_boundary.geojson.
"""

MARKETS = {
    'heights': {
        'html': 'index.html',
        'permits_json': 'heights_permits.json',
        'zips': ['77008', '77009', '77007'],
        'boundary': 'heights_boundary.geojson',
        'coord_box': (29.70, 29.90, -95.50, -95.30),
        'east_lng': -95.370,
        'enabled': True,
    },
    'montrose': {
        'html': 'montrose.html',
        'permits_json': 'montrose_permits.json',
        'zips': ['77006', '77019', '77098'],
        'boundary': 'montrose_boundary.geojson',
        'coord_box': (29.714, 29.773, -95.421, -95.372),
        'east_lng': None,
        'enabled': True,
    },
    'westu': {
        'html': 'westu.html',
        'permits_json': 'westu_permits.json',
        'zips': ['77005'],
        'boundary': None,          # all of 77005 by design; zip + box guard
        'coord_box': (29.696, 29.735, -95.458, -95.408),
        'east_lng': None,
        'enabled': True,
    },
    'riveroaks': {
        'html': 'riveroaks.html',
        'permits_json': 'riveroaks_permits.json',
        'zips': ['77019'],
        'boundary': 'riveroaks_boundary.geojson',
        'coord_box': (29.732, 29.776, -95.457, -95.400),
        'east_lng': None,
        'enabled': True,
    },
    'springbranch': {
        'html': 'springbranch.html',
        'permits_json': 'springbranch_permits.json',
        'zips': ['77055', '77080', '77043'],
        'boundary': 'springbranch_boundary.geojson',
        'coord_box': (29.771, 29.844, -95.568, -95.441),
        'east_lng': None,
        'enabled': True,
    },
    'timbergrove': {
        'html': 'timbergrove.html',
        'permits_json': 'timbergrove_permits.json',
        'zips': ['77008'],
        'boundary': 'timbergrove_boundary.geojson',
        'coord_box': (29.773, 29.825, -95.469, -95.401),
        'east_lng': None,
        'enabled': True,
    },
    'gardenoaksoakforest': {
        'html': 'gardenoaksoakforest.html',
        'permits_json': 'gardenoaksoakforest_permits.json',
        'zips': ['77018', '77092'],
        'boundary': 'gardenoaksoakforest_boundary.geojson',
        'coord_box': (29.803, 29.848, -95.492, -95.390),
        'east_lng': None,
        'enabled': True,
    },
    # Permit ingest stays off. HAR refresh uses the municipal boundary.
    'springvalley': {
        'html': 'springvalley.html',
        'permits_json': None,
        'zips': ['77024'],
        'boundary': 'springvalley_boundary.geojson',
        'coord_box': (29.7735, 29.8089, -95.5304, -95.4763),
        'east_lng': None,
        'enabled': False,
    },
}

# ingest order: heights first (established), then worst-staleness order.
# springvalley is omitted until a permits file exists.
INGEST_ORDER = ['heights', 'montrose', 'westu', 'riveroaks', 'springbranch',
                'timbergrove', 'gardenoaksoakforest']

# Weekly HAR pass. Heights keeps sold_ingest.py / active_ingest.py so a
# multi-zip export cannot replace the Heights snapshot.
HAR_MARKETS = ['montrose', 'westu', 'riveroaks', 'springbranch', 'springvalley',
               'timbergrove', 'gardenoaksoakforest']

ALL_ZIPS = sorted({z for m in MARKETS.values() if m['enabled'] for z in m['zips']})
