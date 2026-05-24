# @generated [partially] Gemini: comments
# pylint: disable=no-member
"""Detection logic for finding targets using OpenCV"""
from pathlib import Path
import cv2
import numpy as np


class BaseDetector:
    """Base class for image analysis"""

    # Sentinel-2 resolution is approximately 10m x 10m per pixel.
    # Area of 1 pixel = 100 square meters = 0.0001 square kilometers.
    PIXEL_AREA_KM2 = 0.0001

    def __init__(self, target_name: str):
        self.target_name = target_name

    def __str__(self) -> str:
        """Returns string representation of the detector."""
        return f"Detector for target: {self.target_name}"

    def analyze(self, image_path: Path) -> float:
        """
        Reads the pre-calculated mask and returns the detected area in square kilometers
        """
        # Read image using OpenCV (loads as Grayscale (b&w)  format )
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")

        # water/forest - 255 (white)  everything  >127 rounds to 255 to make it white on photo
        _, mask = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

        return self._calculate_area(mask)

    def _calculate_area(self, mask: np.ndarray) -> float:
        """Calculates the area based on the number of positive pixels in the mask"""
        # count all pixels that are white (255) in the mask
        pixel_count = cv2.countNonZero(mask)
        return pixel_count * self.PIXEL_AREA_KM2


class WaterDetector(BaseDetector):
    """Detector for water bodies using NDWI masks"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        super().__init__("water")


class ForestDetector(BaseDetector):
    """Detector for forest/vegetation using NDVI masks"""
    # pylint: disable=too-few-public-methods
    def __init__(self):
        super().__init__("forest")
