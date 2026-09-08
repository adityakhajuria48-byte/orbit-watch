# Orbit Watch — Python prediction engine

The website runs this real Python code in a dedicated Pyodide Web Worker. It uses the `sgp4` library to propagate CelesTrak OMM records. The rest of the interface and live two-second radar remain React/TypeScript and satellite.js. No Python web server or Visual Studio installation is required to use the published pass timeline.

The first calculation downloads the pinned Pyodide 0.29.4 runtime from jsDelivr. Coordinates and orbital records are passed to Python locally, not uploaded to a prediction server. If that download is blocked, the timeline shows an error and offers retry; the radar and world map remain independent. The pinned pure-Python sgp4 2.27 wheel is served by this website.

## Run with regular Python

Requires Python 3.10 or later:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s . -p 'test_*.py'
python orbit_engine.py catalog.json --lat 28.6139 --lon 77.2090 --radius 45 --hours 6 --ids 25544,20580,49260
```

`catalog.json` must be the JSON array from CelesTrak's active OMM catalog:
https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=json
Do not pass the website API wrapper; extract its `data` array first.

## Numerical method and limitations

SGP4 returns TEME positions. Greenwich sidereal rotation and WGS84 geodetic conversion produce the subpoint, matching the existing satellite.js convention. Distances are great-circle distances on a mean-radius Earth (6371.0088 km), not slant distances or visibility predictions. Samples are 30 seconds apart; local minima and edge intervals are refined, including short grazing passes. Entry/exit boundaries are bisected to within 0.25 seconds. That numerical tolerance is not a statement of physical orbital accuracy. TLE/OMM age, maneuvers and Earth approximations still affect results.

Records more than 7 days from the computation time are excluded. If a pass continues beyond a prediction window, its duration is marked as a lower bound. The browser exposes featured missions, favorites, the selected satellite, and the entire active catalog, with 1/6/24-hour windows. Full-catalog scans can take minutes on slower devices, show partial progress, and can be cancelled. Changing the location, radius, catalog or selection invalidates results.

The timeline runs only while the website is open. It does not schedule Telegram notifications. The existing independent Cloudflare checker under `alerts/` handles closed-browser notifications after its credentials and hosting are configured; API v3 adds selected-satellite filtering.

Source documentation: https://pypi.org/project/sgp4/ and https://pyodide.org/en/0.29.4/usage/webworker.html
