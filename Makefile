install:
	pip install -r requirements.txt

run-water:
	python -m geochange analyze water --lat 50.08 --lon 14.42 --start 2018 --end 2023 --mosaic

run-forest:
	python -m geochange analyze forest --lat 49.94 --lon 14.18 --start 2018 --end 2023 --mosaic

test:
	python -m pytest tests/ -v --cov=geochange