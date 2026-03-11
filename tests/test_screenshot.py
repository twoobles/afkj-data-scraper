"""Tests for extraction.screenshot module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from config import (
    GAME_WINDOW_HEIGHT,
    GAME_WINDOW_WIDTH,
    SCROLL_SIMILARITY_THRESHOLD,
)
from extraction.screenshot import (
    capture_region,
    find_game_window,
    save_debug_screenshot,
    screenshots_match,
    verify_window_size,
)

# ---------------------------------------------------------------------------
# find_game_window
# ---------------------------------------------------------------------------


def _mock_window(title, left=100, top=200, width=1295, height=757):
    w = MagicMock()
    w.title = title
    w.left = left
    w.top = top
    w.width = width
    w.height = height
    return w


@patch("extraction.screenshot.sleep", return_value=None)
@patch("extraction.screenshot.gw")
def test_find_game_window_returns_region(mock_gw, _mock_sleep):
    win = _mock_window("AFK Journey: Homestead")
    mock_gw.getWindowsWithTitle.return_value = [win]

    result = find_game_window()

    assert result == (100, 200, 1295, 757)


@patch("extraction.screenshot.gw")
def test_find_game_window_no_windows(mock_gw):
    mock_gw.getWindowsWithTitle.return_value = []

    assert find_game_window() is None


@patch("extraction.screenshot.gw")
def test_find_game_window_no_exact_title_match(mock_gw):
    win = _mock_window("AFK Journey: Homestead - Other")
    mock_gw.getWindowsWithTitle.return_value = [win]

    assert find_game_window() is None


@patch("extraction.screenshot.sleep", return_value=None)
@patch("extraction.screenshot.gw")
def test_find_game_window_picks_exact_match_from_multiple(mock_gw, _mock_sleep):
    wrong = _mock_window("AFK Journey: Homestead (2)", left=0, top=0)
    right = _mock_window("AFK Journey: Homestead", left=50, top=60)
    mock_gw.getWindowsWithTitle.return_value = [wrong, right]

    result = find_game_window()

    assert result == (50, 60, 1295, 757)


# ---------------------------------------------------------------------------
# verify_window_size
# ---------------------------------------------------------------------------


def test_verify_window_size_correct():
    region = (0, 0, GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT)
    assert verify_window_size(region) is True


def test_verify_window_size_wrong_width():
    region = (0, 0, GAME_WINDOW_WIDTH + 1, GAME_WINDOW_HEIGHT)
    assert verify_window_size(region) is False


def test_verify_window_size_wrong_height():
    region = (0, 0, GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT + 1)
    assert verify_window_size(region) is False


def test_verify_window_size_ignores_position():
    region = (999, 999, GAME_WINDOW_WIDTH, GAME_WINDOW_HEIGHT)
    assert verify_window_size(region) is True


# ---------------------------------------------------------------------------
# capture_region (to be implemented)
# ---------------------------------------------------------------------------


def test_capture_region_returns_numpy_array():
    """capture_region should return a BGR numpy array."""
    region = (0, 0, 100, 100)
    try:
        result = capture_region(region)
    except NotImplementedError:
        pytest.skip("capture_region not yet implemented")

    assert isinstance(result, np.ndarray)
    assert result.ndim == 3
    assert result.shape[2] == 3  # BGR channels


def test_capture_region_matches_requested_size():
    """Returned array dimensions should match the requested width/height."""
    region = (0, 0, 200, 150)
    try:
        result = capture_region(region)
    except NotImplementedError:
        pytest.skip("capture_region not yet implemented")

    assert result.shape[0] == 150  # height
    assert result.shape[1] == 200  # width


# ---------------------------------------------------------------------------
# screenshots_match (to be implemented)
# ---------------------------------------------------------------------------


def test_screenshots_match_identical():
    """Two identical images should be considered matching."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    try:
        result = screenshots_match(img, img.copy())
    except NotImplementedError:
        pytest.skip("screenshots_match not yet implemented")

    assert result == True  # noqa: E712 — numpy bool


def test_screenshots_match_completely_different():
    """Two completely different images should not match."""
    black = np.zeros((100, 100, 3), dtype=np.uint8)
    white = np.full((100, 100, 3), 255, dtype=np.uint8)
    try:
        result = screenshots_match(black, white)
    except NotImplementedError:
        pytest.skip("screenshots_match not yet implemented")

    assert result == False  # noqa: E712 — numpy bool


def test_screenshots_match_near_threshold():
    """Images just above the similarity threshold should match."""
    img = np.full((100, 100, 3), 128, dtype=np.uint8)
    # Flip a tiny fraction of pixels — well under the (1 - threshold) tolerance
    changed = img.copy()
    num_changed = max(1, int(100 * 100 * (1 - SCROLL_SIMILARITY_THRESHOLD) * 0.5))
    changed.flat[: num_changed * 3] = 0
    try:
        result = screenshots_match(img, changed)
    except NotImplementedError:
        pytest.skip("screenshots_match not yet implemented")

    assert result == True  # noqa: E712 — numpy bool


# ---------------------------------------------------------------------------
# save_debug_screenshot (to be implemented)
# ---------------------------------------------------------------------------


def test_save_debug_screenshot_creates_dir_and_file(tmp_path, monkeypatch):
    """save_debug_screenshot should create DEBUG_DIR and write a file."""
    monkeypatch.setattr("extraction.screenshot.DEBUG_DIR", tmp_path / "debug_out")
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    try:
        save_debug_screenshot(img, "test_label")
    except NotImplementedError:
        pytest.skip("save_debug_screenshot not yet implemented")

    debug_dir = tmp_path / "debug_out"
    assert debug_dir.exists()
    saved_files = list(debug_dir.iterdir())
    assert len(saved_files) == 1
    assert "test_label" in saved_files[0].name


def test_save_debug_screenshot_uses_label_in_filename(tmp_path, monkeypatch):
    """The saved filename should contain the provided label."""
    monkeypatch.setattr("extraction.screenshot.DEBUG_DIR", tmp_path / "debug_out")
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    try:
        save_debug_screenshot(img, "my_custom_label")
    except NotImplementedError:
        pytest.skip("save_debug_screenshot not yet implemented")

    saved = list((tmp_path / "debug_out").iterdir())
    assert any("my_custom_label" in f.name for f in saved)
