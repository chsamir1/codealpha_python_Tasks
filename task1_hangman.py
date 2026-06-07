"""
CodeAlpha Internship — Task 1: Hangman Game
Author  : [Your Name]
Purpose : Text-based Hangman with visual ASCII gallows, hint system,
          score tracking, and replay support.
"""

import random
import os

# ─────────────────────────────────────────────
#  Word bank  (category → words)
# ─────────────────────────────────────────────
WORD_BANK: dict[str, list[str]] = {
    "Technology" : ["python", "keyboard", "algorithm", "database", "network"],
    "Animals"    : ["elephant", "crocodile", "butterfly", "penguin", "cheetah"],
    "Countries"  : ["germany", "australia", "pakistan", "argentina", "vietnam"],
    "Sports"     : ["volleyball", "badminton", "swimming", "cricket", "cycling"],
    "Science"    : ["gravity", "molecule", "electron", "nucleus", "friction"],
}

MAX_WRONG = 6   # maximum incorrect guesses allowed

# ─────────────────────────────────────────────
#  ASCII gallows stages  (0 = empty → 6 = full)
# ─────────────────────────────────────────────
GALLOWS = [
    """
  +---+
  |   |
      |
      |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
      |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
  |   |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========
""",
    """
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========
""",
]


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pick_word() -> tuple[str, str]:
    """Return a random (category, word) pair."""
    category = random.choice(list(WORD_BANK.keys()))
    word     = random.choice(WORD_BANK[category])
    return category, word


def build_display(word: str, guessed: set[str]) -> str:
    """Return the word with unguessed letters replaced by underscores."""
    return "  ".join(letter if letter in guessed else "_" for letter in word)


def get_hint(word: str, guessed: set[str]) -> str:
    """Reveal one unguessed letter as a hint (costs nothing, one-time use)."""
    hidden = [ch for ch in word if ch not in guessed]
    return random.choice(hidden) if hidden else ""


def render(word: str, guessed: set[str], wrong: set[str],
           category: str, hint_used: bool) -> None:
    clear_screen()
    print("=" * 45)
    print("          🎯  H A N G M A N")
    print("=" * 45)
    print(GALLOWS[len(wrong)])
    print(f"  Category : {category}")
    print(f"  Word     : {build_display(word, guessed)}")
    print(f"  Wrong    : {len(wrong)}/{MAX_WRONG}   "
          f"Letters tried: {', '.join(sorted(wrong)) or 'none'}")
    print(f"  Hint     : {'already used' if hint_used else 'type  ?  to reveal a letter'}")
    print("=" * 45)


def play_round(score: int) -> int:
    """Play one full round; return updated score."""
    category, word = pick_word()
    guessed: set[str] = set()
    wrong:   set[str] = set()
    hint_used          = False

    while True:
        render(word, guessed, wrong, category, hint_used)

        # ── Win check ──────────────────────────────
        if all(ch in guessed for ch in word):
            points = max(10, 30 - len(wrong) * 4)
            print(f"\n  ✅  You won!  The word was '{word.upper()}'")
            print(f"  🏆  +{points} points  (total: {score + points})")
            return score + points

        # ── Lose check ─────────────────────────────
        if len(wrong) >= MAX_WRONG:
            print(f"\n  ❌  Game over!  The word was '{word.upper()}'")
            print(f"  📊  Score unchanged: {score}")
            return score

        # ── Input ──────────────────────────────────
        raw = input("\n  Guess a letter (or ? for hint): ").strip().lower()

        if raw == "?":
            if hint_used:
                input("  ⚠  Hint already used. Press Enter…")
            else:
                hint_letter = get_hint(word, guessed)
                if hint_letter:
                    guessed.add(hint_letter)
                    hint_used = True
                    input(f"  💡  Hint: '{hint_letter}' has been revealed. Press Enter…")
            continue

        if len(raw) != 1 or not raw.isalpha():
            input("  ⚠  Enter a single letter. Press Enter…")
            continue

        if raw in guessed or raw in wrong:
            input(f"  ⚠  '{raw}' already tried. Press Enter…")
            continue

        if raw in word:
            guessed.add(raw)
        else:
            wrong.add(raw)


def main() -> None:
    score = 0
    print("\n  Welcome to Hangman! 🎉")
    print("  Guess the hidden word before the man is hanged.")
    print("  You have 6 wrong attempts per round.\n")
    input("  Press Enter to start…")

    while True:
        score = play_round(score)
        again = input("\n  Play again? (y / n): ").strip().lower()
        if again != "y":
            break

    clear_screen()
    print("\n" + "=" * 45)
    print(f"  Thanks for playing!  Final Score: {score}")
    print("=" * 45 + "\n")


if __name__ == "__main__":
    main()
