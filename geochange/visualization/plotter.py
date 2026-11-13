# @generated [partially] Gemini: comments
"""Plotting utilities for generating trend graphs"""
from pathlib import Path
import matplotlib.pyplot as plt


def plot_trend(results: dict, target_name: str, lat: float, lon: float, output_path: Path) -> None:
    """
    Generates and saves a line chart showing the  area trend

    :param results: Dictionary mapping years to areas ({2018: 12.5, ...})
    :param target_name: The name of the target ("water" or "forest")
    :param lat: Latitude of the center point
    :param lon: Longitude of the center point
    :param output_path: Path where the  plot will be saved
    """
    years = list(results.keys())
    areas = list(results.values())

    plt.figure(figsize=(10, 6))

    # plot color based on the target
    color = "blue" if target_name == "water" else "green"

    # Plot the data points and connecting line
    plt.plot(years, areas, marker='o', linestyle='-', color=color, linewidth=2, markersize=8)

    # Configure chart title and axis labels
    plt.title(f"Trend of {target_name.capitalize()} Area at Lat: {lat}, Lon: {lon}", fontsize=14, pad=15)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel("Area (km²)", fontsize=12)
    plt.xticks(years)

    # grid for better readability
    plt.grid(True, linestyle='--', alpha=0.7)

    # Save the plot to file path with 'high' resolution (300 DPI)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
