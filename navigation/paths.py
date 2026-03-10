"""Data-driven navigation paths for each game mode.

Each path is a sequence of steps to reach a mode's ranking screen
from the main menu. Steps reference template image names that
the navigator will click in order.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class NavStep:
    """A single navigation step — click a UI element identified by template matching.

    Attributes:
        template_name: Filename of the template image to locate and click.
        description: Human-readable description for logging.
    """

    template_name: str
    description: str


# Navigation paths from main menu to each mode's ranking screen.
# Order of steps matters — they are executed sequentially.
NAV_PATHS: dict[str, list[NavStep]] = {
    "afk_stages": [
        # TODO: Define steps once template images are captured
    ],
    "dream_realm": [],
    "supreme_arena": [],
    "arcane_labyrinth": [],
    "honor_duel": [],
}

# Path to return from any ranking screen back to the main menu.
NAV_BACK_PATH: list[NavStep] = [
    # TODO: Define back-navigation steps
]
