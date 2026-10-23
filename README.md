# python-google-maps-routing-api

A python client library for Google Maps Routes API.

See <https://developers.google.com/maps/documentation/routes>

Only API keys are supported, see <https://developers.google.com/maps/documentation/routes/client-library>

## Usage

```python
import asyncio

import aiohttp

from google_maps_routing_api import GoogleMapsRoutingApi, TravelMode


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        api = GoogleMapsRoutingApi(session=session, api_key="...", referrer="https://example.com/")
        response = await api.async_compute_routes(
            origin="Mountain View, CA",
            destination="San Francisco, CA",
            travel_mode=TravelMode.DRIVE,
        )
        for route in response.routes:
            print(route.duration, route.distance_meters, route.localized_values.duration.text)


asyncio.run(main())
```

## Development environment

```sh
python3 -m venv .venv
source .venv/bin/activate
# for Windows CMD:
# .venv\Scripts\activate.bat
# for Windows PowerShell:
# .venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -e .

# Run pre-commit
python -m pip install pre-commit
pre-commit install
pre-commit run --all-files

# Run tests
python -m pip install -e ".[test]"
pytest

# Build package
python -m pip install build
python -m build
```
