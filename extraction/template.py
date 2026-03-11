"""Template matching utilities using OpenCV."""

import logging

import cv2  # noqa: F401
import numpy as np

from config import TEMPLATE_CONFIDENCE_THRESHOLD, TEMPLATES_DIR  # noqa: F401

logger = logging.getLogger(__name__)


def load_template(template_name: str) -> np.ndarray:
    """Load a template image from the templates directory.

    Args:
        template_name: Filename of the template image (e.g. "rank_menu_button.png").

    Returns:
        Template as a numpy array (BGR, OpenCV format).

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return cv2.imread(str(path))


def find_template(
    screenshot: np.ndarray,
    template: np.ndarray,
    threshold: float = TEMPLATE_CONFIDENCE_THRESHOLD,
) -> tuple[int, int] | None:
    """Find the best match for a template in a screenshot.

    Args:
        screenshot: The full screenshot to search (BGR numpy array).
        template: The template image to find (BGR numpy array).
        threshold: Minimum confidence for a valid match.

    Returns:
        Center (x, y) of the best match, or None if confidence is below threshold.
    """
    match = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(match)

    if max_val < threshold:
        return None
    template_height, template_width = template.shape[:2]
    center_x = max_loc[0] + template_width // 2
    center_y = max_loc[1] + template_height // 2
    return (center_x, center_y)


def find_all_templates(
    screenshot: np.ndarray,
    template: np.ndarray,
    threshold: float = TEMPLATE_CONFIDENCE_THRESHOLD,
) -> list[tuple[int, int]]:
    """Find all non-overlapping matches for a template in a screenshot.

    Useful for locating multiple ranking cards in a single screenshot.

    Args:
        screenshot: The full screenshot to search (BGR numpy array).
        template: The template image to find (BGR numpy array).
        threshold: Minimum confidence for a valid match.

    Returns:
        List of center (x, y) positions for each match, sorted top-to-bottom.
    """
    match = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(match >= threshold)

    def _too_close(point, accepted, template_width, template_height):
        for a in accepted:
            if abs(point[0] - a[0]) < template_width and abs(point[1] - a[1]) < template_height:
                return True
        return False

    accepted, centers = [], []
    template_height, template_width = template.shape[:2]
    for point in zip(*locations[::-1], strict=True):
        if not _too_close(point, accepted, template_width, template_height):
            accepted.append(point)
            center_x = point[0] + template_width // 2
            center_y = point[1] + template_height // 2
            centers.append((center_x, center_y))

    return sorted(centers, key=lambda c: c[1])
