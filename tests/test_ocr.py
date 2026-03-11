"""Tests for extraction.ocr module."""

from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from extraction.ocr import (
    extract_text_lines,
    get_reader,
    parse_rank,
    parse_score,
    parse_stage,
    read_text,
)

FAKE_IMAGE = np.zeros((100, 300, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# get_reader
# ---------------------------------------------------------------------------


@patch("extraction.ocr.easyocr")
def test_get_reader_initializes_once(mock_easyocr):
    """Reader should be created once and reused on subsequent calls."""
    import extraction.ocr as ocr_module

    ocr_module._reader = None  # Reset
    mock_reader = MagicMock()
    mock_easyocr.Reader.return_value = mock_reader

    reader1 = get_reader()
    reader2 = get_reader()

    assert reader1 is mock_reader
    assert reader2 is mock_reader
    mock_easyocr.Reader.assert_called_once()

    ocr_module._reader = None  # Cleanup


# ---------------------------------------------------------------------------
# read_text
# ---------------------------------------------------------------------------


@patch("extraction.ocr.get_reader")
def test_read_text_returns_raw_results(mock_get_reader):
    mock_reader = MagicMock()
    mock_reader.readtext.return_value = [
        ([[0, 0], [50, 0], [50, 20], [0, 20]], "1", 0.95),
        ([[60, 0], [200, 0], [200, 20], [60, 20]], "PlayerOne", 0.88),
    ]
    mock_get_reader.return_value = mock_reader

    results = read_text(FAKE_IMAGE)

    assert len(results) == 2
    assert results[0][1] == "1"
    assert results[1][1] == "PlayerOne"
    mock_reader.readtext.assert_called_once()


# ---------------------------------------------------------------------------
# extract_text_lines
# ---------------------------------------------------------------------------


@patch("extraction.ocr.read_text")
def test_extract_text_lines_sorted_top_to_bottom(mock_read):
    # Simulate detections at different y positions (top of bounding box)
    mock_read.return_value = [
        ([[0, 50], [100, 50], [100, 70], [0, 70]], "GuildName", 0.85),
        ([[0, 10], [100, 10], [100, 30], [0, 30]], "PlayerName", 0.90),
        ([[0, 0], [30, 0], [30, 15], [0, 15]], "1", 0.95),
    ]

    lines = extract_text_lines(FAKE_IMAGE)

    assert lines == ["1", "PlayerName", "GuildName"]


@patch("extraction.ocr.read_text")
def test_extract_text_lines_filters_low_confidence(mock_read):
    mock_read.return_value = [
        ([[0, 0], [30, 0], [30, 15], [0, 15]], "1", 0.95),
        ([[0, 20], [100, 20], [100, 40], [0, 40]], "garbage", 0.15),
    ]

    lines = extract_text_lines(FAKE_IMAGE)

    assert "garbage" not in lines
    assert "1" in lines


# ---------------------------------------------------------------------------
# parse_rank
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1", 1),
        ("42", 42),
        ("100", 100),
        # Common OCR misreads
        ("O1", 1),  # O → 0, leading zero stripped
        ("l2", 12),  # l → 1
        ("1O3", 103),  # O → 0
    ],
)
def test_parse_rank_valid(text, expected):
    assert parse_rank(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "abc",
        "12.5",
        "rank",
        "#1",
    ],
)
def test_parse_rank_invalid(text):
    assert parse_rank(text) is None


# ---------------------------------------------------------------------------
# parse_score
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("169B", "169B"),
        ("210M", "210M"),
        ("42K", "42K"),
        ("7T", "7T"),
        # Case normalization
        ("169b", "169B"),
        ("210m", "210M"),
    ],
)
def test_parse_score_valid(text, expected):
    assert parse_score(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "169",
        "abc",
        "B169",
        "169X",
        "1.5B",
    ],
)
def test_parse_score_invalid(text):
    assert parse_score(text) is None


# ---------------------------------------------------------------------------
# parse_stage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1452", "1452"),
        ("A252", "A252"),
        # Apex prefix from game UI
        ("Apex 252", "A252"),
        ("Apex252", "A252"),
        ("apex 252", "A252"),
        # Common OCR misreads
        ("a252", "A252"),  # lowercase a
        ("4252", "4252"),  # OCR read A as 4 — valid plain number
    ],
)
def test_parse_stage_valid(text, expected):
    assert parse_stage(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "abc",
        "A",
        "Apex",
        "12.5",
        "stage",
    ],
)
def test_parse_stage_invalid(text):
    assert parse_stage(text) is None
