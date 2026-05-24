# @generated [partially] Gemini: comments
import pytest
import sys
from geochange.cli import parse_arguments

def test_parse_arguments_valid(mocker):
    """Test that the parser correctly reads valid CLI arguments"""
    # 1. Fake the terminal input
    test_args = ["geochange", "analyze", "water", "--lat", "50.08", "--lon", "14.42", "--start", "2018", "--end", "2023", "--mosaic"]
    mocker.patch.object(sys, 'argv', test_args)

    # 2. Run the parser
    args = parse_arguments()

    # 3. Verify it understood everything correctly
    assert args.command == "analyze"
    assert args.target == "water"
    assert args.lat == 50.08
    assert args.lon == 14.42
    assert args.start == 2018
    assert args.end == 2023
    assert args.mosaic is True

def test_parse_arguments_missing_required(mocker):
    """Test that missing required arguments raises an exit error"""
    # Missing --lat and --lon
    test_args = ["geochange", "analyze", "water", "--start", "2018", "--end", "2023"]
    mocker.patch.object(sys, 'argv', test_args)

    # argparse uses SystemExit to stop the program if args are wrong
    with pytest.raises(SystemExit):
        parse_arguments()