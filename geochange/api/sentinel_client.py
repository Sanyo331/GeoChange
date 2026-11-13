# @generated [partially] Gemini: refactor of evalscript (big problems with linter)
# of mosaicing concept and comments
"""Sentinel Hub API client for downloading satellite imagery"""

from pathlib import Path
import requests
from geochange.config import SETTINGS
from geochange.logger import logger


class SentinelClient:
    """Client for interacting with the Sentinel Hub API to download satellite images"""

    AUTH_URL = "https://services.sentinel-hub.com/oauth/token"
    PROCESS_URL = "https://services.sentinel-hub.com/api/v1/process"

    def __init__(self):
        """Initialize client and fetch authentication credentials from config."""
        self.client_id = SETTINGS["api"]["sentinel_client_id"]
        self.client_secret = SETTINGS["api"]["sentinel_client_secret"]
        self.token = None

    def authenticate(self) -> None:
        """Fetches the OAuth2 token from Sentinel Hub and stores"""
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(self.AUTH_URL, data=payload, timeout=30)
        response.raise_for_status()  # Will raise an exception if the request fails (401 Unauthorized)

        self.token = response.json().get("access_token")
        logger.info("Successfully authenticated with Sentinel Hub API.")

    # pylint: disable=too-many-locals
    def _get_evalscript(self, image_type: str, use_mosaic: bool) -> tuple[str, str]:
        """Generates the appropriate JavaScript evalscript and expected image format"""
        if use_mosaic:
            if image_type == "water_mask":
                return ("""
                //VERSION=3
                function setup() { return { input: ["B03", "B08", "dataMask"], output: { bands: 1 }, mosaicking: "ORBIT" }; }
                function evaluatePixel(samples) {
                    let values = [];
                    for (let i = 0; i < samples.length; i++) {
                        if (samples[i].dataMask === 1) {
                            let ndwi = (samples[i].B03 - samples[i].B08) / (samples[i].B03 + samples[i].B08);
                            values.push(ndwi);
                        }
                    }
                    if (values.length === 0) return [0]; 
                    values.sort(function(a, b){return a - b}); 
                    let median = values[Math.floor(values.length / 2)];
                    return [median > 0.1 ? 1 : 0]; 
                }
                """, "image/png")

            if image_type == "forest_mask":
                return ("""
                //VERSION=3
                function setup() { return { input: ["B04", "B08", "dataMask"], output: { bands: 1 }, mosaicking: "ORBIT" }; }
                function evaluatePixel(samples) {
                    let values = [];
                    for (let i = 0; i < samples.length; i++) {
                        if (samples[i].dataMask === 1) {
                            let ndvi = (samples[i].B08 - samples[i].B04) / (samples[i].B08 + samples[i].B04);
                            values.push(ndvi);
                        }
                    }
                    if (values.length === 0) return [0];
                    values.sort(function(a, b){return a - b});
                    let median = values[Math.floor(values.length / 2)];
                    return [median > 0.5 ? 1 : 0]; 
                }
                """, "image/png")

            if image_type == "photo":
                return ("""
                //VERSION=3
                function setup() { return { input: ["B02", "B03", "B04", "dataMask"], output: { bands: 3 }, mosaicking: "ORBIT" }; }
                function evaluatePixel(samples) {
                    let r = [], g = [], b = [];
                    for (let i = 0; i < samples.length; i++) {
                        if (samples[i].dataMask === 1) {
                            r.push(samples[i].B04); g.push(samples[i].B03); b.push(samples[i].B02);
                        }
                    }
                    if (r.length === 0) return [0, 0, 0];
                    r.sort(function(a,b){return a-b}); g.sort(function(a,b){return a-b}); b.sort(function(a,b){return a-b});
                    let mid = Math.floor(r.length / 2);
                    return [2.5 * r[mid], 2.5 * g[mid], 2.5 * b[mid]];
                }
                """, "image/jpeg")

        else:
            if image_type == "water_mask":
                return ("""//VERSION=3
                function setup() { return { input: ["B03", "B08", "dataMask"], output: { bands: 1 } }; }
                function evaluatePixel(sample) { return [(sample.B03 - sample.B08) / (sample.B03 + sample.B08) > 0.1 ? 1 : 0]; }
                """, "image/png")

            if image_type == "forest_mask":
                return ("""//VERSION=3
                function setup() { return { input: ["B04", "B08", "dataMask"], output: { bands: 1 } }; }
                function evaluatePixel(sample) { return [(sample.B08 - sample.B04) / (sample.B08 + sample.B04) > 0.5 ? 1 : 0]; }
                """, "image/png")

            if image_type == "photo":
                return ("""//VERSION=3
                function setup() { return { input: ["B02", "B03", "B04", "dataMask"], output: { bands: 3 } }; }
                function evaluatePixel(sample) { return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02]; }
                """, "image/jpeg")

        raise ValueError(f"Unknown image_type: {image_type}")

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def _build_payload(self, bbox: list[float], year: int, lat: float, img_format: str, evalscript: str) -> dict:
        """Helper method to construct the API request payload"""
        if lat >= 0:
            start_md = SETTINGS["analysis"]["northern_hemisphere"]["start_month_day"]
            end_md = SETTINGS["analysis"]["northern_hemisphere"]["end_month_day"]
        else:
            start_md = SETTINGS["analysis"]["southern_hemisphere"]["start_month_day"]
            end_md = SETTINGS["analysis"]["southern_hemisphere"]["end_month_day"]

        return {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"}
                },
                "data": [{
                    "type": "sentinel-2-l2a",
                    "dataFilter": {
                        "timeRange": {
                            "from": f"{year}-{start_md}T00:00:00Z",
                            "to": f"{year}-{end_md}T23:59:59Z"
                        },
                        "maxCloudCoverage": SETTINGS["analysis"]["max_cloud_coverage"]
                    }
                }]
            },
            "output": {
                "width": 512,
                "height": 512,
                "responses": [{"identifier": "default", "format": {"type": img_format}}]
            },
            "evalscript": evalscript
        }

    def download_image(self, coords: tuple[float, float], year: int, output_path: Path, options: dict) -> None:
        """Downloads a satellite image based on provided coordinates, year, and options"""
        lat, lon = coords
        image_type = options.get("image_type", "water_mask")

        if not self.token:
            self.authenticate()

        # Get the JavaScript and format based on options
        evalscript, img_format = self._get_evalscript(image_type, options.get("use_mosaic", False))

        # Build payload directly, calculating the bounding box inline (delta = 0.05)
        request_payload = self._build_payload(
            [lon - 0.05, lat - 0.05, lon + 0.05, lat + 0.05],
            year,
            lat,
            img_format,
            evalscript
        )

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        logger.info("Downloading %s for %d (Lat: %s, Lon: %s)...", image_type, year, lat, lon)

        response = requests.post(self.PROCESS_URL, json=request_payload, headers=headers, timeout=30)

        if response.status_code != 200:
            logger.error("API Error %s: %s", response.status_code, response.text)
            raise RuntimeError(f"API Error {response.status_code}: {response.text}")

        with open(output_path, "wb") as file:
            file.write(response.content)

        logger.info("Successfully saved to %s", output_path)
