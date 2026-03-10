"""Tests for config module."""

from pathlib import Path

import config


def test_base_dir_is_project_root():
    assert Path(__file__).resolve().parent.parent == config.BASE_DIR


def test_subdirectories_are_under_base():
    assert config.TEMPLATES_DIR == config.BASE_DIR / "templates"
    assert config.DEBUG_DIR == config.BASE_DIR / "debug"
    assert config.TEST_DATA_DIR == config.BASE_DIR / "test_data"
    assert config.DB_PATH == config.BASE_DIR / "scans.db"


def test_game_modes_list():
    assert "afk_stages" in config.GAME_MODES
    assert "dream_realm" in config.GAME_MODES
    assert "supreme_arena" in config.GAME_MODES
    assert "arcane_labyrinth" in config.GAME_MODES
    assert "honor_duel" in config.GAME_MODES
    assert len(config.GAME_MODES) == 5


def test_mode_columns_keys_match_game_modes():
    assert set(config.MODE_COLUMNS.keys()) == set(config.GAME_MODES)


def test_mode_columns_afk_stages_has_extra():
    rank_col, extras = config.MODE_COLUMNS["afk_stages"]
    assert rank_col == "afk_rank"
    assert "afk_stage" in extras


def test_mode_columns_dream_realm_has_extra():
    rank_col, extras = config.MODE_COLUMNS["dream_realm"]
    assert rank_col == "dr_rank"
    assert "dr_score" in extras


def test_mode_columns_rank_only_modes_have_no_extras():
    for mode in ["supreme_arena", "arcane_labyrinth", "honor_duel"]:
        _, extras = config.MODE_COLUMNS[mode]
        assert extras == [], f"{mode} should have no extra columns"


def test_template_confidence_is_sane():
    assert 0 < config.TEMPLATE_CONFIDENCE_THRESHOLD < 1


def test_scroll_similarity_is_sane():
    assert 0 < config.SCROLL_SIMILARITY_THRESHOLD <= 1
