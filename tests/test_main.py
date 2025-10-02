#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Hangman (Python CLI Game)
File: test_main.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-02
Updated: 2025-10-02
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
Pytest unit tests covering core Hangman engine behavior:
win path, mistake counting, repeat/invalid guess handling, and masked rendering.

Usage:
pytest -q

Notes:
- Tests import and exercise HangmanEngine only (no I/O).
- Keep tests deterministic by controlling the word list and max mistakes.
"""



from hangman_game.main import HangmanEngine


def test_engine_win_path():
    engine = HangmanEngine(words=["abc"], max_mistakes=6)
    state = engine.new_game()
    # guess a, then b, then c
    for g in "abc":
        state = engine.guess(state, g)
    assert state.won is True
    assert state.finished is True
    assert state.lost is False
    assert state.mistakes == 0


def test_engine_counts_mistakes_and_repeats_are_ignored():
    engine = HangmanEngine(words=["abc"], max_mistakes=2)
    s = engine.new_game()

    # wrong guess
    s = engine.guess(s, "x")
    assert s.mistakes == 1
    assert "x" in s.guessed

    # repeat wrong guess (ignored)
    s2 = engine.guess(s, "x")
    assert s2.mistakes == 1
    assert s2 is s  # engine returns same state on repeats/invalids

    # invalid input ignored
    s3 = engine.guess(s, "xy")
    assert s3 is s

    # wrong guess to lose
    s = engine.guess(s, "y")
    assert s.lost is True
    assert s.finished is True


def test_masked_representation_and_wrong_letters():
    engine = HangmanEngine(words=["banana"], max_mistakes=6)
    s = engine.new_game()
    s = engine.guess(s, "b")
    s = engine.guess(s, "x")
    assert s.masked.replace(" ", "") == "b_____"
    assert s.wrong_letters == {"x"}
