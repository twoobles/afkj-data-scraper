"""Screen capture utilities for the game window."""

import logging
from time import sleep

import cv2
import numpy as np
import pygetwindow as gw
from PIL import ImageGrab

from config import (
    DEBUG_DIR,
    GAME_WINDOW_HEIGHT,
    GAME_WINDOW_TITLE,
    GAME_WINDOW_WIDTH,
    SCROLL_SIMILARITY_THRESHOLD,
)

logger = logging.getLogger(__name__)

def find_game_window() -> tuple[int, int, int, int] | None:
    """Locate the game window and return its bounding box (left, top, width, height).

    Returns None if the window is not found.
    """
    windows = gw.getWindowsWithTitle(GAME_WINDOW_TITLE)
    if not windows:
        return None
    window = next((w for w in windows if w.title == GAME_WINDOW_TITLE), None)
    if not window:
        return None

    sleep(1)

    return (window.left, window.top, window.width, window.height)


def verify_window_size(region: tuple[int, int, int, int]) -> bool:
    """Check that the game window matches the expected resolution.

    Args:
        region: Bounding box (left, top, width, height) from find_game_window.

    Returns:
        True if width and height match GAME_WINDOW_WIDTH/HEIGHT.
    """
    window_width, window_height = region[2], region[3]
    return (window_width == GAME_WINDOW_WIDTH) and (window_height == GAME_WINDOW_HEIGHT)


def capture_region(region: tuple[int, int, int, int]) -> np.ndarray:
    """Capture a screenshot of the specified screen region.

    Args:
        region: Bounding box (left, top, width, height) to capture.

    Returns:
        Screenshot as a numpy array (BGR, OpenCV format).
    """
    left, top, width, height = region
    bbox = (left, top, left + width, top + height)
    screenshot = ImageGrab.grab(bbox=bbox)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def screenshots_match(img_a: np.ndarray, img_b: np.ndarray) -> bool:
    """Compare two screenshots to detect end-of-list (no change after scroll).

    Uses pixel-level similarity against SCROLL_SIMILARITY_THRESHOLD.

    Args:
        img_a: First screenshot (BGR numpy array).
        img_b: Second screenshot (BGR numpy array).

    Returns:
        True if images are similar enough to indicate no new content.
    """
    similarity = np.count_nonzero(img_a == img_b) / img_a.size
    return similarity >= SCROLL_SIMILARITY_THRESHOLD


def save_debug_screenshot(image: np.ndarray, label: str) -> None:
    """Save a screenshot to the debug directory for inspection.

    Only called when --debug is active. Creates DEBUG_DIR if needed.

    Args:
        image: Screenshot as BGR numpy array.
        label: Descriptive label used in the filename.
    """
    DEBUG_DIR.mkdir(exist_ok=True)
    filepath = str(DEBUG_DIR / f"{label}.png")
    cv2.imwrite(filepath, image)
