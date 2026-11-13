# @generated [partially] Gemini:  bug fix for ThreadPoolExecution and comments
"""Command-line interface and main execution logic for GeoChange"""
import argparse
import csv
import concurrent.futures
from pathlib import Path
from geochange.api.sentinel_client import SentinelClient
from geochange.analysis.detector import WaterDetector, ForestDetector
from geochange.visualization.plotter import plot_trend
from geochange.logger import logger


def parse_arguments() -> argparse.Namespace:
    """Parses CLI arguments and returns them"""
    parser = argparse.ArgumentParser(
        description="GeoChange: Track environmental changes from satellite imagery."
    )

    # Subparsers to allow multiple commands
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: 'analyze'
    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze changes in a specific area over time."
    )

    # Positional argument
    analyze_parser.add_argument(
        "target", choices=["water", "forest"], help="Target object to detect (water or forest)."
    )

    # Optional arguments (flags) required for the analysis
    analyze_parser.add_argument("--lat", type=float, required=True, help="Latitude of the center point.")
    analyze_parser.add_argument("--lon", type=float, required=True, help="Longitude of the center point.")
    analyze_parser.add_argument("--start", type=int, required=True, help="Start year (e.g., 2018).")
    analyze_parser.add_argument("--end", type=int, required=True, help="End year (e.g., 2023).")
    analyze_parser.add_argument("--mosaic", action="store_true", help="Use median mosaicking for the season.")

    return parser.parse_args()


def download_data(client: SentinelClient, args: argparse.Namespace, mode_str: str) -> None:
    """Handles concurrent downloading of images and masks"""
    masks_dir, photos_dir = Path("data/masks"), Path("data/photos")
    masks_dir.mkdir(parents=True, exist_ok=True)
    photos_dir.mkdir(parents=True, exist_ok=True)

    tasks = []
    loc_str = f"{args.lat}_{args.lon}"
    for year in range(args.start, args.end + 1):
        mask_file = masks_dir / f"mask_{args.target}_{mode_str}_{loc_str}_{year}.png"
        photo_file = photos_dir / f"photo_{mode_str}_{loc_str}_{year}.jpg"

        if not mask_file.exists():
            tasks.append((year, mask_file, f"{args.target}_mask"))
        if not photo_file.exists():
            tasks.append((year, photo_file, "photo"))

    if not tasks:
        logger.info("All necessary files already exist locally.")
        return

    logger.info("Starting concurrent download of %d files...", len(tasks))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            # Note: passing coordinates as a tuple to satisfy Pylint
            executor.submit(client.download_image, (args.lat, args.lon), t[0], t[1],
                            {"image_type": t[2], "use_mosaic": args.mosaic})
            for t in tasks
        ]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except RuntimeError as err:
                logger.error("Download failed: %s", err)


def run_analysis(args: argparse.Namespace, mode_str: str) -> None:
    """Analyzes images, saves CSV, and generates plot"""
    detector = WaterDetector() if args.target == "water" else ForestDetector()
    results = {}
    masks_dir = Path("data/masks")
    loc_str = f"{args.lat}_{args.lon}"

    for year in range(args.start, args.end + 1):
        img_path = masks_dir / f"mask_{args.target}_{mode_str}_{loc_str}_{year}.png"
        if img_path.exists():
            area = detector.analyze(img_path)
            results[year] = area
            logger.info("Year %d: Detected %s area = %.2f km²", year, args.target, area)
        else:
            logger.warning("Mask for %d not found.", year)

    csv_file = Path("data") / f"{args.target}_{loc_str}_{mode_str}_results.csv"
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Year", "Area_km2"])
        for year, area in results.items():
            writer.writerow([year, round(area, 4)])

    plot_file = Path("data") / f"{args.target}_{loc_str}_{mode_str}_trend.png"
    plot_trend(results, args.target, args.lat, args.lon, plot_file)


def main():
    """Main entry point of the CLI application"""
    # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    args = parse_arguments()

    # Basic input validation
    if not -90 <= args.lat <= 90:
        logger.error("Latitude must be between -90 and 90.")
        return
    if not -180 <= args.lon <= 180:
        logger.error("Longitude must be between -180 and 180.")
        return
    if args.start > args.end:
        logger.error("Start year cannot be greater than end year.")
        return

    if args.command == "analyze":
        # basic info to verify arguments and configs
        mode_str = "mosaic" if args.mosaic else "simple"
        logger.info("Initializing GeoChange | Target: %s | Mode: %s", args.target, mode_str)

        try:
            client = SentinelClient()
            client.authenticate()
            if client.token:
                download_data(client, args, mode_str)
                logger.info("Starting OpenCV analysis...")
                run_analysis(args, mode_str)
                logger.info("Analysis Complete!")
        except RuntimeError as err:
            logger.error("Application error: %s", err)

    if __name__ == "__main__":
        main()
