"""OCR text extraction from ranking card screenshots using EasyOCR."""

import logging
import re

import easyocr
import numpy as np

from config import (
    OCR_CONFIDENCE_THRESHOLD,
    OCR_LANGUAGES,
    SCORE_PATTERN,
    STAGE_PATTERN,
    STAGE_PREFIX,
)

logger = logging.getLogger(__name__)

# Module-level reader instance, initialized lazily on first use.
_reader = None


def get_reader() -> easyocr.Reader:
    """Return the shared EasyOCR reader, initializing on first call.

    Returns:
        easyocr.Reader instance configured with OCR_LANGUAGES.
    """
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(OCR_LANGUAGES)
    return _reader


def read_text(image: np.ndarray) -> list[tuple[list, str, float]]:
    """Run OCR on an image region and return raw EasyOCR results.

    Args:
        image: Cropped image region (BGR numpy array).

    Returns:
        List of EasyOCR detections: (bounding_box, text, confidence).
    """
    reader = get_reader()
    return reader.readtext(image)


def extract_text_lines(image: np.ndarray) -> list[str]:
    """Run OCR and return just the text strings, sorted top-to-bottom.

    Filters out low-confidence results. Useful for extracting
    structured text from a ranking card region.

    Args:
        image: Cropped image region (BGR numpy array).

    Returns:
        List of detected text strings, ordered by vertical position.
    """
    results = read_text(image)
    lines = []
    for entry in sorted(results, key=lambda f: f[0][0][1]):
        _, text, confidence = entry
        if confidence >= OCR_CONFIDENCE_THRESHOLD:
            lines.append(text)
    return lines


def parse_rank(text: str) -> int | None:
    """Parse a rank number from OCR text.

    Handles common OCR misreads (e.g. 'O' → '0', 'l' → '1').

    Args:
        text: Raw OCR text that should contain a rank number.

    Returns:
        Parsed integer rank, or None if text is not a valid rank.
    """
    rank = text.translate(str.maketrans("Ol", "01"))

    try:
        return int(rank)
    except (ValueError, TypeError):
        return None


def parse_score(text: str) -> str | None:
    """Parse a Dream Realm score from OCR text (e.g. '169B', '210M').

    Args:
        text: Raw OCR text that should contain a score.

    Returns:
        Normalized score string (e.g. '169B'), or None if invalid.
    """
    if SCORE_PATTERN.match(text):
        return text.upper()
    return None


def parse_stage(text: str) -> str | None:
    """Parse an AFK Stages stage from OCR text (e.g. '1452', 'Apex 252').

    Normalizes Apex prefix variants ('Apex 252', 'apex252', 'A252') to 'A' shorthand.

    Args:
        text: Raw OCR text that should contain a stage number.

    Returns:
        Normalized stage string, or None if invalid.
    """
    if STAGE_PATTERN.match(text):
        stage = re.sub(r"^A(pex)?\s*", "", text, flags=re.IGNORECASE)
        if text[0].isalpha():
            return STAGE_PREFIX + stage
        return stage
    return None
