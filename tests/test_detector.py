# @generated [partially] Gemini: comments
import cv2
import numpy as np
import pytest
from geochange.analysis.detector import WaterDetector


def test_detector_calculates_correct_area(tmp_path):
    """
    Test that the detector correctly calculates area from a known image mask
    We use 'tmp_path', a built-in pytest fixture for creating temporary files
    """
    # 1. Create a completely black 100x100 pixel image (0 same as 'no target')
    dummy_img = np.zeros((100, 100), dtype=np.uint8)

    # 2. Draw a white 10x10 pixel square (255 means target area detected)
    # 10 * 10 = 100 target pixels
    dummy_img[0:10, 0:10] = 255

    # 3. Save this dummy image to a temporary folder
    test_image_path = tmp_path / "fake_mask.png"
    cv2.imwrite(str(test_image_path), dummy_img)

    # 4. Initialize and run the detector
    detector = WaterDetector()
    area = detector.analyze(test_image_path)

    # 5. Verify the mathematical logic:
    # 1 pixel = 0.0001 km²
    # 100 pixels * 0.0001 = 0.01 km²
    assert area == pytest.approx(0.01)


def test_detector_file_not_found():
    """Test that the detector raises a FileNotFoundError if the image doesn't exist"""
    detector = WaterDetector()

    # Verify that the program raises the correct exception for a missing file
    with pytest.raises(FileNotFoundError):
        detector.analyze("non_existent_file.png")