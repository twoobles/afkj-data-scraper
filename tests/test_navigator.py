"""Tests for navigation.navigator module."""

from unittest.mock import patch

import numpy as np

from config import NAV_CLICK_DELAY_SEC, SCROLL_CLICKS, SCROLL_PAUSE_SEC
from navigation.navigator import (
    _execute_step,
    navigate_back,
    navigate_to_mode,
    scroll_ranking_list,
)
from navigation.paths import NavStep

GAME_REGION = (100, 200, 800, 600)
FAKE_SCREENSHOT = np.zeros((600, 800, 3), dtype=np.uint8)
FAKE_TEMPLATE = np.zeros((50, 50, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# _execute_step
# ---------------------------------------------------------------------------


@patch("navigation.navigator.sleep")
@patch("navigation.navigator.pyautogui")
@patch("navigation.navigator.find_template", return_value=(400, 300))
@patch("navigation.navigator.load_template", return_value=FAKE_TEMPLATE)
@patch("navigation.navigator.capture_region", return_value=FAKE_SCREENSHOT)
def test_execute_step_success(mock_capture, mock_load, mock_find, mock_gui, mock_sleep):
    step = NavStep(template_name="btn.png", description="Click button")
    result = _execute_step(step, GAME_REGION)

    assert result is True
    mock_capture.assert_called_once_with(GAME_REGION)
    mock_load.assert_called_once_with("btn.png")
    mock_find.assert_called_once_with(FAKE_SCREENSHOT, FAKE_TEMPLATE)
    # Click at screen coords: game_region offset + template match
    mock_gui.click.assert_called_once_with(100 + 400, 200 + 300)
    mock_sleep.assert_called_once_with(NAV_CLICK_DELAY_SEC)


@patch("navigation.navigator.sleep")
@patch("navigation.navigator.pyautogui")
@patch("navigation.navigator.find_template", return_value=None)
@patch("navigation.navigator.load_template", return_value=FAKE_TEMPLATE)
@patch("navigation.navigator.capture_region", return_value=FAKE_SCREENSHOT)
def test_execute_step_template_not_found(mock_capture, mock_load, mock_find, mock_gui, mock_sleep):
    step = NavStep(template_name="missing.png", description="Missing button")
    result = _execute_step(step, GAME_REGION)

    assert result is False
    mock_gui.click.assert_not_called()
    mock_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# navigate_to_mode
# ---------------------------------------------------------------------------


@patch("navigation.navigator._execute_step", return_value=True)
@patch(
    "navigation.navigator.NAV_PATHS",
    {
        "test_mode": [
            NavStep("step1.png", "First step"),
            NavStep("step2.png", "Second step"),
        ]
    },
)
def test_navigate_to_mode_success(mock_step):
    result = navigate_to_mode("test_mode", GAME_REGION)

    assert result is True
    assert mock_step.call_count == 2
    mock_step.assert_any_call(NavStep("step1.png", "First step"), GAME_REGION)
    mock_step.assert_any_call(NavStep("step2.png", "Second step"), GAME_REGION)


@patch("navigation.navigator._execute_step")
@patch(
    "navigation.navigator.NAV_PATHS",
    {
        "test_mode": [
            NavStep("step1.png", "First step"),
            NavStep("step2.png", "Second step"),
        ]
    },
)
def test_navigate_to_mode_fails_at_second_step(mock_step):
    mock_step.side_effect = [True, False]
    result = navigate_to_mode("test_mode", GAME_REGION)

    assert result is False
    assert mock_step.call_count == 2


def test_navigate_to_mode_unknown_mode():
    result = navigate_to_mode("nonexistent_mode", GAME_REGION)
    assert result is False


@patch("navigation.navigator._execute_step")
@patch("navigation.navigator.NAV_PATHS", {"empty_mode": []})
def test_navigate_to_mode_empty_steps(mock_step):
    result = navigate_to_mode("empty_mode", GAME_REGION)

    assert result is False
    mock_step.assert_not_called()


# ---------------------------------------------------------------------------
# navigate_back
# ---------------------------------------------------------------------------


@patch("navigation.navigator._execute_step", return_value=True)
@patch(
    "navigation.navigator.NAV_BACK_PATH",
    [NavStep("back1.png", "Back step 1"), NavStep("back2.png", "Back step 2")],
)
def test_navigate_back_success(mock_step):
    result = navigate_back(GAME_REGION)

    assert result is True
    assert mock_step.call_count == 2


@patch("navigation.navigator._execute_step")
@patch(
    "navigation.navigator.NAV_BACK_PATH",
    [NavStep("back1.png", "Back step 1"), NavStep("back2.png", "Back step 2")],
)
def test_navigate_back_fails(mock_step):
    mock_step.side_effect = [True, False]
    result = navigate_back(GAME_REGION)

    assert result is False


@patch("navigation.navigator._execute_step")
@patch("navigation.navigator.NAV_BACK_PATH", [])
def test_navigate_back_no_steps(mock_step):
    result = navigate_back(GAME_REGION)

    assert result is False
    mock_step.assert_not_called()


# ---------------------------------------------------------------------------
# scroll_ranking_list
# ---------------------------------------------------------------------------


@patch("navigation.navigator.sleep")
@patch("navigation.navigator.pyautogui")
def test_scroll_ranking_list(mock_gui, mock_sleep):
    scroll_ranking_list(GAME_REGION)

    # Center of GAME_REGION: (100 + 800//2, 200 + 600//2) = (500, 500)
    mock_gui.moveTo.assert_called_once_with(500, 500)
    mock_gui.scroll.assert_called_once_with(SCROLL_CLICKS)
    mock_sleep.assert_called_once_with(SCROLL_PAUSE_SEC)


@patch("navigation.navigator.sleep")
@patch("navigation.navigator.pyautogui")
def test_scroll_ranking_list_different_region(mock_gui, mock_sleep):
    region = (0, 0, 1000, 500)
    scroll_ranking_list(region)

    mock_gui.moveTo.assert_called_once_with(500, 250)
    mock_gui.scroll.assert_called_once_with(SCROLL_CLICKS)
