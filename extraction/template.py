"""Template matching utilities using OpenCV."""

import logging

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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError
