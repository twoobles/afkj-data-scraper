"""Screen capture utilities for the game window."""

import logging

import numpy as np
from PIL import Image  # noqa: F401

from config import DEBUG_DIR, GAME_WINDOW_HEIGHT, GAME_WINDOW_WIDTH  # noqa: F401

logger = logging.getLogger(__name__)


def find_game_window() -> tuple[int, int, int, int] | None:
    """Locate the game window and return its bounding box (left, top, width, height).

    Returns None if the window is not found.
    """
    raise NotImplementedError


def verify_window_size(region: tuple[int, int, int, int]) -> bool:
    """Check that the game window matches the expected resolution.

    Args:
        region: Bounding box (left, top, width, height) from find_game_window.

    Returns:
        True if width and height match GAME_WINDOW_WIDTH/HEIGHT.
    """
    raise NotImplementedError


def capture_region(region: tuple[int, int, int, int]) -> np.ndarray:
    """Capture a screenshot of the specified screen region.

    Args:
        region: Bounding box (left, top, width, height) to capture.

    Returns:
        Screenshot as a numpy array (BGR, OpenCV format).
    """
    raise NotImplementedError


def screenshots_match(img_a: np.ndarray, img_b: np.ndarray) -> bool:
    """Compare two screenshots to detect end-of-list (no change after scroll).

    Uses pixel-level similarity against SCROLL_SIMILARITY_THRESHOLD.

    Args:
        img_a: First screenshot (BGR numpy array).
        img_b: Second screenshot (BGR numpy array).

    Returns:
        True if images are similar enough to indicate no new content.
    """
    raise NotImplementedError


def save_debug_screenshot(image: np.ndarray, label: str) -> None:
    """Save a screenshot to the debug directory for inspection.

    Only called when --debug is active. Creates DEBUG_DIR if needed.

    Args:
        image: Screenshot as BGR numpy array.
        label: Descriptive label used in the filename.
    """
    raise NotImplementedError
