# 🕯️ The Last Whisper

A small horror-themed Hangman game where the player has to discover a cursed word before the darkness takes over.

The game includes atmospheric backgrounds, sound effects, background music, difficulty levels, a hint system, scoring, and different win/lose scenes.

---

## 🎮 Features

- 👻 Horror-themed Hangman gameplay
- 🎯 Three difficulty levels:
  - Easy
  - Medium
  - Hard
- 🔤 Interactive A–Z letter buttons
- 💡 Hint system
- 🏆 Score system
- 💀 Different win and lose screens
- 🔊 Background music
- 🎵 Sound effects for:
  - Correct guesses
  - Wrong guesses
  - Game start
  - Winning
  - Losing
  - Background movement
- 🔇 Mute / unmute button
- 🔄 Replay option
- 🌌 Horror background artwork
- 🪦 Progressive Hangman animation
- 📖 Local word lists as fallback
- 🌐 Browser version
- 🐍 Python/Pygame version

---

## 🕹️ How to Play

The objective is simple:

> Guess the hidden word before the Hangman is completed.

At the beginning of the game, select a difficulty level.

The game then chooses a word and hides its letters.

Click or press letters to guess the word.

### Correct Guess

If the selected letter exists in the word:

- The letter is revealed.
- A correct-guess sound is played.
- Your game continues.

### Wrong Guess

If the letter is not present:

- A mistake is counted.
- The Hangman progresses.
- A wrong-guess sound is played.

If all allowed mistakes are used, the game ends.

---

## 💡 Hint System

The game includes a hint button.

A hint reveals one unrevealed letter from the current word.

Using a hint decreases the player's score depending on the selected difficulty.

---

## 🏆 Scoring

The game uses different scores depending on the difficulty.

| Difficulty | Win Score | Lose Penalty | Hint Cost |
|------------|-----------|--------------|-----------|
| Easy       | 250       | 75           | 40        |
| Medium     | 500       | 175          | 90        |
| Hard       | 900       | 350          | 160       |

The scoring values can be changed from the game source code.

---

## 🎚️ Difficulty

### Easy

Designed for a simpler game experience.

### Medium

Uses longer words and higher scoring.

### Hard

Uses the longest words and provides the highest possible score.

The Python version uses different word lengths for each difficulty.

---

## 🎵 Audio

The game uses several audio files to create the atmosphere:

```text
BackgroundMusic_Start.ogg
BackgroundMusic_Gameplay.ogg
BackgroundMusic_Win.ogg
BackgroundMusic_Lose.ogg
BushMovement.ogg
Correct.ogg
Wrong.ogg
Screech1.ogg
