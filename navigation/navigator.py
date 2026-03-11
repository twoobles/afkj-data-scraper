"""Screen navigator — clicks through UI using template matching."""

import logging
from time import sleep

import pyautogui

from config import NAV_CLICK_DELAY_SEC, SCROLL_CLICKS, SCROLL_PAUSE_SEC
from extraction.screenshot import capture_region
from extraction.template import find_template, load_template
from navigation.paths import NAV_BACK_PATH, NAV_PATHS, NavStep

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
    if mode not in NAV_PATHS:
        return False

    steps = NAV_PATHS[mode]
    if not steps:
        return False

    return all(_execute_step(step, game_region) for step in steps)


def navigate_back(game_region: tuple[int, int, int, int]) -> bool:
    """Navigate back to the main menu from any ranking screen.

    Args:
        game_region: Bounding box of the game window (left, top, width, height).

    Returns:
        True if navigation succeeded, False if any step failed.
    """
    if not NAV_BACK_PATH:
        return False

    return all(_execute_step(step, game_region) for step in NAV_BACK_PATH)


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
    screenshot = capture_region(game_region)
    template = load_template(step.template_name)
    match = find_template(screenshot, template)
    if match is None:
        return False

    pyautogui.click(game_region[0] + match[0], game_region[1] + match[1])
    sleep(NAV_CLICK_DELAY_SEC)
    return True


def scroll_ranking_list(game_region: tuple[int, int, int, int]) -> None:
    """Scroll down the ranking list by the configured amount.

    Uses pyautogui.scroll with SCROLL_CLICKS, then pauses for SCROLL_PAUSE_SEC.

    Args:
        game_region: Bounding box of the game window (for mouse positioning).
    """
    center_x = game_region[0] + game_region[2] // 2
    center_y = game_region[1] + game_region[3] // 2
    pyautogui.moveTo(center_x, center_y)
    pyautogui.scroll(SCROLL_CLICKS)
    sleep(SCROLL_PAUSE_SEC)
