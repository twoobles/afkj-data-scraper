"""Screen navigator — clicks through UI using template matching."""

import logging

from navigation.paths import NAV_BACK_PATH, NAV_PATHS, NavStep  # noqa: F401

logger = logging.getLogger(__name__)


def navigate_to_mode(
    mode: str,
    game_region: tuple[int, int, int, int],
) -> bool:
    """Navigate from the main menu to a mode's ranking screen.

    Follows the step sequence defined in NAV_PATHS for the given mode.
    Each step: capture screenshot → find template → click center → wait.

    Args:
        mode: Game mode name (must be a key in NAV_PATHS).
        game_region: Bounding box of the game window (left, top, width, height).

    Returns:
        True if navigation succeeded, False if any step failed.
    """
    raise NotImplementedError


def navigate_back(game_region: tuple[int, int, int, int]) -> bool:
    """Navigate back to the main menu from any ranking screen.

    Args:
        game_region: Bounding box of the game window (left, top, width, height).

    Returns:
        True if navigation succeeded, False if any step failed.
    """
    raise NotImplementedError


def _execute_step(
    step: NavStep,
    game_region: tuple[int, int, int, int],
) -> bool:
    """Execute a single navigation step: find template and click it.

    Args:
        step: The navigation step to execute.
        game_region: Bounding box of the game window.

    Returns:
        True if the template was found and clicked.
    """
    raise NotImplementedError


def scroll_ranking_list(game_region: tuple[int, int, int, int]) -> None:
    """Scroll down the ranking list by the configured amount.

    Uses pyautogui.scroll with SCROLL_CLICKS, then pauses for SCROLL_PAUSE_SEC.

    Args:
        game_region: Bounding box of the game window (for mouse positioning).
    """
    raise NotImplementedError
