# GeoChange

## Topic
GeoChange is a CLI application that automatically tracks and analyzes environmental changes in a specific area on Earth over time (e.g., drying up of water bodies or deforestation). It downloads satellite imagery using public APIs (Sentinel Hub) and analyzes the area using OpenCV and Numpy. The output includes console statistics, CSV data export, and a generated trend plot.

## Core Features
* **Smart Satellite Data Fetching:** Automatically determines the correct hemisphere's summer season and downloads images with low cloud coverage.
* **Scientific Indices Analysis:** Uses NDWI (Normalized Difference Water Index) and NDVI (Normalized Difference Vegetation Index) for precise detection.
* **Median Mosaicking:** Optionally generates cloud-free synthetic images by calculating the median pixel values over a season.
* **Caching System:** Prevents redundant API calls by locally storing downloaded masks and true-color photos.

## Necessary dependencies
Dependencies are listed in `requirements.txt`. Install them using:
```bash
pip install -r requirements.txt
```

Note: You must create a config.yaml file in the root directory with your Sentinel Hub API credentials. See config.example.yaml for reference.

## How to start it
The application is run via the command line interface:
```bash
python -m geochange analyze <target> --lat <latitude> --lon <longitude> --start <year> --end <year> [--mosaic]
```

Track water drying up in Prague:
```bash
python -m geochange analyze water --lat 50.08 --lon 14.42 --start 2018 --end 2025
```

Track deforestation using advanced median mosaicking:
```bash
python -m geochange analyze forest --lat 49.94 --lon 14.18 --start 2018 --end 2023 --mosaic
```

Alternatively, you can use the built-in Makefile:
```bash 
make run-water
make run-forest
```

# How to run tests
```bash
make test
```
or

```bash
python -m pytest tests/ -v --cov=geochange
```
