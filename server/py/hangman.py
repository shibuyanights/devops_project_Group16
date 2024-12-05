from typing import List, Optional
import random
from enum import Enum
from server.py.game import Game, Player


class GuessLetterAction:
    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()

    def __repr__(self):
        return f"GuessLetterAction(letter={self.letter})"


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:
    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess.upper()
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses

    def is_word_guessed(self) -> bool:
        """ Check if all letters in the word have been guessed """
        return all(letter in self.guesses for letter in self.word_to_guess)

    def has_max_incorrect_guesses(self) -> bool:
        """ Check if max incorrect guesses have been reached """
        return len(self.incorrect_guesses) >= 8


class Hangman(Game):
    def __init__(self) -> None:
        """ Initialize the game with no state """
        self._state: Optional[HangmanGameState] = None

    def get_state(self) -> HangmanGameState:
        """ Return the current game state """
        if not self._state:
            raise ValueError("Game state has not been set!")
        return self._state

    def set_state(self, state: HangmanGameState) -> None:
        """ Set the game to a specific state """
        self._state = state

    def print_state(self) -> None:
        """ Print the current state with guessed letters revealed """
        if not self._state:
            raise ValueError("Game state has not been set!")
        masked_word = ''.join(
            [letter if letter in self._state.guesses else '_' for letter in self._state.word_to_guess]
        )
        print(f"Word: {masked_word} | Phase: {self._state.phase} | Guesses: {self._state.guesses} | Incorrect: {self._state.incorrect_guesses}")

    def get_list_action(self) -> List[GuessLetterAction]:
        """ Get a list of unused letters as possible actions """
        if not self._state:
            raise ValueError("Game state has not been set!")
        guessed_letters = set(self._state.guesses + self._state.incorrect_guesses)
        unused_letters = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") - guessed_letters
        return [GuessLetterAction(letter) for letter in unused_letters]

    def apply_action(self, action: GuessLetterAction) -> None:
        """ Apply the guessed letter to the game """
        if not self._state:
            raise ValueError("Game state has not been set!")
        guessed_letter = action.letter
        if guessed_letter in self._state.guesses or guessed_letter in self._state.incorrect_guesses:
            return  # Letter already guessed

        if guessed_letter in self._state.word_to_guess:
            self._state.guesses.append(guessed_letter)
        else:
            self._state.incorrect_guesses.append(guessed_letter)

        # Check if the game should end
        if self._state.is_word_guessed():
            self._state.phase = GamePhase.FINISHED
        elif self._state.has_max_incorrect_guesses():
            self._state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Return the game state as seen by the player """
        return self.get_state()


class RandomPlayer(Player):
    def select_action(self, state: HangmanGameState, actions: List[GuessLetterAction]) -> Optional[GuessLetterAction]:
        """ Select a random action from the available actions """
        if actions:
            return random.choice(actions)
        return None


if __name__ == "__main__":
    # Initialize the game
    game = Hangman()
    game_state = HangmanGameState(word_to_guess='DevOps', phase=GamePhase.RUNNING, guesses=[], incorrect_guesses=[])
    game.set_state(game_state)

    # Simulate a simple gameplay loop
    player = RandomPlayer()
    while game.get_state().phase == GamePhase.RUNNING:
        possible_actions = game.get_list_action()
        chosen_action = player.select_action(game.get_state(), possible_actions)
        if chosen_action:
            game.apply_action(chosen_action)
            game.print_state()

    # End of the game
    print("Game Over!")

