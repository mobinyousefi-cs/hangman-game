#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=========================================================================================================
Project: Hangman (Python CLI Game)
File: main.py
Author: Mobin Yousefi (GitHub: https://github.com/mobinyousefi-cs)
Created: 2025-10-02
Updated: 2025-10-02
License: MIT License (see LICENSE file for details)
=========================================================================================================

Description:
A clean, testable command-line implementation of the classic Hangman game.
Includes a pure engine (`HangmanEngine`) for unit testing and a CLI loop with ASCII art,
custom word-list support, and reproducible runs via random seed.

Usage:
python -m hangman_game [--wordlist PATH] [--max-mistakes N] [--seed INT]
# or, after installation:
hangman [--wordlist PATH] [--max-mistakes N] [--seed INT]

Notes:
- No external dependencies (stdlib only).
- Provide a newline-delimited word list via --wordlist for custom vocabularies.
- ASCII hangman frames scale with mistake count; default max mistakes = 6.
- Designed for a modern src/ layout with Ruff/Black/pytest CI.
"""


from __future__ import annotations

import argparse
import random
import sys
import time
from dataclasses import dataclass, field
from typing import Iterable, Set


# Minimal, family-friendly default vocabulary. You can pass a custom wordlist via --wordlist.
_DEFAULT_WORDS = (
    "python",
    "variable",
    "function",
    "algorithm",
    "optimization",
    "network",
    "matrix",
    "iterator",
    "package",
    "generator",
    "computation",
    "notebook",
    "research",
    "datastructure",
    "recursion",
    "scheduling",
    "fog",
    "cloud",
    "bytecode",
    "protocol",
)

# ASCII frames for fun — indexed by number of mistakes
_HANGMAN_FRAMES = [
    r"""
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    /    |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    / \  |
         |
    =========""",
]


@dataclass
class GameState:
    """Immutable-ish snapshot of the game state suitable for rendering & testing."""
    secret: str
    max_mistakes: int
    guessed: Set[str] = field(default_factory=set)
    mistakes: int = 0
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None

    @property
    def masked(self) -> str:
        """Word with unknown letters as underscores, spaced for readability."""
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    @property
    def wrong_letters(self) -> Set[str]:
        return {g for g in self.guessed if g not in self.secret}

    @property
    def remaining(self) -> int:
        return self.max_mistakes - self.mistakes

    @property
    def won(self) -> bool:
        return all(ch in self.guessed for ch in self.secret)

    @property
    def lost(self) -> bool:
        return self.mistakes >= self.max_mistakes

    @property
    def finished(self) -> bool:
        return self.won or self.lost

    def duration(self) -> float | None:
        end = self.ended_at if self.ended_at is not None else time.time()
        return end - self.started_at if end else None


class HangmanEngine:
    """Encapsulates core game logic (pure-ish, testable)."""

    def __init__(
        self,
        words: Iterable[str] = _DEFAULT_WORDS,
        max_mistakes: int = 6,
        rng: random.Random | None = None,
    ) -> None:
        vocab = [w.strip().lower() for w in words if w and w.strip()]
        if not vocab:
            raise ValueError("Word list must not be empty.")
        self._words = [w for w in vocab if w.isalpha()]
        if not self._words:
            raise ValueError("Word list must contain at least one alphabetic word.")
        self._max_mistakes = max(1, int(max_mistakes))
        self._rng = rng or random.Random()

    def new_game(self) -> GameState:
        secret = self._rng.choice(self._words)
        return GameState(secret=secret, max_mistakes=self._max_mistakes)

    def guess(self, state: GameState, raw: str) -> GameState:
        """Apply a guess and return the next state (doesn't mutate input)."""
        if state.finished:
            return state

        letter = (raw or "").strip().lower()
        if not (len(letter) == 1 and letter.isalpha()):
            # Ignore invalid guesses silently; caller can message the user.
            return state

        if letter in state.guessed:
            return state

        guessed = set(state.guessed)
        guessed.add(letter)

        mistakes = state.mistakes + (0 if letter in state.secret else 1)
        ended_at = time.time() if (mistakes >= state.max_mistakes or all(c in guessed for c in state.secret)) else None

        return GameState(
            secret=state.secret,
            max_mistakes=state.max_mistakes,
            guessed=guessed,
            mistakes=mistakes,
            started_at=state.started_at,
            ended_at=ended_at,
        )


def _load_words_from_file(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        words = []
        for line in f:
            w = line.strip().lower()
            if w and w.isalpha():
                words.append(w)
        return words


def play(
    words: Iterable[str] | None = None,
    max_mistakes: int = 6,
    seed: int | None = None,
) -> int:
    """Interactive CLI loop. Returns process exit code (0=win, 1=loss)."""
    rng = random.Random(seed)
    engine = HangmanEngine(words=words or _DEFAULT_WORDS, max_mistakes=max_mistakes, rng=rng)
    state = engine.new_game()

    print("\n=== Hangman — CS Master’s Edition ===")
    print("Guess the secret word. Enter one letter per turn. Ctrl+C to quit.\n")

    while not state.finished:
        frame = _HANGMAN_FRAMES[min(state.mistakes, len(_HANGMAN_FRAMES) - 1)]
        print(frame)
        print(f"\nWord: {state.masked}")
        if state.wrong_letters:
            print(f"Wrong: {', '.join(sorted(state.wrong_letters))}")
        print(f"Attempts left: {state.remaining}")

        raw = input("Your guess: ").strip()
        if not raw:
            print("Please enter a letter (a–z).")
            continue
        next_state = engine.guess(state, raw)
        if next_state is state:
            # Either invalid or repeated guess
            if not (len(raw) == 1 and raw.isalpha()):
                print("Invalid input. Enter a single letter (a–z).")
            elif raw.lower() in state.guessed:
                print(f"You already guessed '{raw.lower()}'.")
        state = next_state
        print()

    # End-of-game screen
    state.ended_at = state.ended_at or time.time()
    frame = _HANGMAN_FRAMES[min(state.mistakes, len(_HANGMAN_FRAMES) - 1)]
    print(frame)
    print(f"\nWord: {' '.join(state.secret)}")
    elapsed = state.duration() or 0.0
    if state.won:
        print("\n🎉 Congratulations! You solved it.")
        print(f"Time: {elapsed:.1f}s | Mistakes: {state.mistakes}/{state.max_mistakes}")
        return 0
    else:
        print("\n💀 Game over. Better luck next time!")
        print(f"The word was: {state.secret}")
        print(f"Time: {elapsed:.1f}s | Mistakes: {state.mistakes}/{state.max_mistakes}")
        return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Play Hangman in your terminal.")
    p.add_argument(
        "--wordlist",
        type=str,
        help="Path to a newline-delimited list of words (letters only).",
    )
    p.add_argument(
        "--max-mistakes",
        type=int,
        default=6,
        help="Number of mistakes allowed before losing (default: 6).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducible games and tests.",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = _build_arg_parser().parse_args(argv)
    words = _load_words_from_file(args.wordlist) if args.wordlist else None
    code = play(words=words, max_mistakes=args.max_mistakes, seed=args.seed)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
