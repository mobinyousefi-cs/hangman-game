# Hangman — Python (CLI)

A clean, testable implementation of the classic Hangman game, designed to match a professional `src/` layout with modern Python packaging and CI.

## Features
- Pure stdlib (no external deps)
- `HangmanEngine` class for unit testing
- Reproducible runs via `--seed`
- Optional custom word list: `--wordlist <path>`
- Ruff + Black + pytest in GitHub Actions

## Quick start
```bash
# 1) Clone
git clone <your-repo-url> hangman
cd hangman

# 2) (Recommended) Create venv
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Install
pip install -e .

# 4) Play!
hangman
# or
python -m hangman_game

# Options
hangman --max-mistakes 8 --seed 42
hangman --wordlist data/words.txt
