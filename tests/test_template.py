"""Tests for extraction.template module."""

import cv2
import numpy as np
import pytest

from extraction.template import find_all_templates, find_template, load_template

# ---------------------------------------------------------------------------
# Helpers — create synthetic test images
# ---------------------------------------------------------------------------


def _make_screenshot(width: int = 400, height: int = 300) -> np.ndarray:
    """Create a random-noise screenshot so template matching behaves realistically."""
    rng = np.random.RandomState(42)
    return rng.randint(0, 256, (height, width, 3), dtype=np.uint8)


def _place_template(screenshot: np.ndarray, template: np.ndarray, x: int, y: int) -> np.ndarray:
    """Paste a template onto a screenshot at (x, y) top-left corner."""
    img = screenshot.copy()
    th, tw = template.shape[:2]
    img[y : y + th, x : x + tw] = template
    return img


def _make_template(width: int = 40, height: int = 30) -> np.ndarray:
    """Create a patterned template distinct from random noise."""
    rng = np.random.RandomState(99)
    return rng.randint(0, 256, (height, width, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# load_template
# ---------------------------------------------------------------------------


def test_load_template_returns_numpy_array(tmp_path, monkeypatch):
    """load_template should return a BGR numpy array from the templates dir."""
    monkeypatch.setattr("extraction.template.TEMPLATES_DIR", tmp_path)
    img = np.full((20, 30, 3), 128, dtype=np.uint8)
    cv2.imwrite(str(tmp_path / "test_btn.png"), img)

    try:
        result = load_template("test_btn.png")
    except NotImplementedError:
        pytest.skip("load_template not yet implemented")

    assert isinstance(result, np.ndarray)
    assert result.shape == (20, 30, 3)


def test_load_template_file_not_found(tmp_path, monkeypatch):
    """load_template should raise FileNotFoundError for missing templates."""
    monkeypatch.setattr("extraction.template.TEMPLATES_DIR", tmp_path)

    try:
        with pytest.raises(FileNotFoundError):
            load_template("nonexistent.png")
    except NotImplementedError:
        pytest.skip("load_template not yet implemented")


# ---------------------------------------------------------------------------
# find_template
# ---------------------------------------------------------------------------


def test_find_template_exact_match():
    """find_template should locate a template placed in the screenshot."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)
    # Place template at top-left (100, 80)
    screenshot = _place_template(screenshot, template, 100, 80)

    try:
        result = find_template(screenshot, template)
    except NotImplementedError:
        pytest.skip("find_template not yet implemented")

    assert result is not None
    cx, cy = result
    # Center should be near (120, 95) — (100 + 40/2, 80 + 30/2)
    assert abs(cx - 120) <= 1
    assert abs(cy - 95) <= 1


def test_find_template_no_match():
    """find_template should return None when the template is absent."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)  # no template placed

    try:
        result = find_template(screenshot, template)
    except NotImplementedError:
        pytest.skip("find_template not yet implemented")

    assert result is None


def test_find_template_below_threshold():
    """find_template should return None when confidence is below threshold."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)

    try:
        # Very high threshold should reject any imperfect match
        result = find_template(screenshot, template, threshold=0.9999)
    except NotImplementedError:
        pytest.skip("find_template not yet implemented")

    assert result is None


def test_find_template_custom_threshold():
    """find_template should respect a custom threshold."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)
    screenshot = _place_template(screenshot, template, 50, 50)

    try:
        result = find_template(screenshot, template, threshold=0.5)
    except NotImplementedError:
        pytest.skip("find_template not yet implemented")

    assert result is not None


# ---------------------------------------------------------------------------
# find_all_templates
# ---------------------------------------------------------------------------


def test_find_all_templates_multiple_matches():
    """find_all_templates should find multiple placed templates."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)
    # Place 3 templates at different y positions (spaced apart)
    screenshot = _place_template(screenshot, template, 100, 20)
    screenshot = _place_template(screenshot, template, 100, 100)
    screenshot = _place_template(screenshot, template, 100, 200)

    try:
        results = find_all_templates(screenshot, template)
    except NotImplementedError:
        pytest.skip("find_all_templates not yet implemented")

    assert len(results) == 3


def test_find_all_templates_sorted_top_to_bottom():
    """Results should be sorted by y-coordinate (top to bottom)."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)
    screenshot = _place_template(screenshot, template, 100, 200)
    screenshot = _place_template(screenshot, template, 100, 20)
    screenshot = _place_template(screenshot, template, 100, 100)

    try:
        results = find_all_templates(screenshot, template)
    except NotImplementedError:
        pytest.skip("find_all_templates not yet implemented")

    ys = [y for _, y in results]
    assert ys == sorted(ys)


def test_find_all_templates_no_matches():
    """find_all_templates should return empty list when nothing matches."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)

    try:
        results = find_all_templates(screenshot, template)
    except NotImplementedError:
        pytest.skip("find_all_templates not yet implemented")

    assert results == []


def test_find_all_templates_returns_centers():
    """Each result should be the center of the matched region."""
    template = _make_template(40, 30)
    screenshot = _make_screenshot(400, 300)
    # Place at (100, 50) — center should be (120, 65)
    screenshot = _place_template(screenshot, template, 100, 50)

    try:
        results = find_all_templates(screenshot, template)
    except NotImplementedError:
        pytest.skip("find_all_templates not yet implemented")

    assert len(results) == 1
    cx, cy = results[0]
    assert abs(cx - 120) <= 1
    assert abs(cy - 65) <= 1
