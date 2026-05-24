# @generated [partially] Gemini: comments
from pathlib import Path
from geochange.visualization.plotter import plot_trend


def test_plot_trend_creates_file(tmp_path):
    """Test that the plotter successfully generates a PNG file with data"""
    # 1. Create fake data
    fake_results = {2018: 10.5, 2019: 11.2, 2020: 10.8}

    # 2. Define a temporary output file
    output_file = tmp_path / "test_plot.png"

    # 3. Call the plotter
    plot_trend(fake_results, "water", 50.0, 14.0, output_file)

    # 4. Verify the file exists and is not empty
    assert output_file.exists()
    assert output_file.stat().st_size > 0