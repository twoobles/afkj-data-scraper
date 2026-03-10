"""Configuration constants for AFK Journey Data Scraper."""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
DEBUG_DIR = BASE_DIR / "debug"
TEST_DATA_DIR = BASE_DIR / "test_data"
DB_PATH = BASE_DIR / "scans.db"

# Game window — expected resolution in windowed mode
GAME_WINDOW_WIDTH = 1920
GAME_WINDOW_HEIGHT = 1080

# Template matching
TEMPLATE_CONFIDENCE_THRESHOLD = 0.8

# Scrolling
SCROLL_CLICKS = -3  # Negative = scroll down
SCROLL_PAUSE_SEC = 0.5  # Pause after each scroll for UI to settle

# End-of-list detection — pixel similarity threshold for consecutive screenshots
SCROLL_SIMILARITY_THRESHOLD = 0.99

# Navigation — wait time after clicking a UI element (seconds)
NAV_CLICK_DELAY_SEC = 1.0

# OCR
OCR_LANGUAGES = ["en", "ch_sim"]

# Google Sheets (actual values loaded from .env at runtime)
SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# All supported game modes
GAME_MODES = [
    "afk_stages",
    "dream_realm",
    "supreme_arena",
    "arcane_labyrinth",
    "honor_duel",
]

# DB column mapping per mode — maps mode name to its (rank_col, extra_cols) in the scans table
MODE_COLUMNS: dict[str, tuple[str, list[str]]] = {
    "afk_stages": ("afk_rank", ["afk_stage"]),
    "dream_realm": ("dr_rank", ["dr_score"]),
    "supreme_arena": ("sa_rank", []),
    "arcane_labyrinth": ("al_rank", []),
    "honor_duel": ("hd_rank", []),
}
