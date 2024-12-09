from typing import List, Optional
import random
from enum import Enum
import logging

logging.basicConfig(level=logging.DEBUG)


class GuessLetterAction:
    def __init__(self, letter: str) -> None:
        self.letter = letter.upper()  # Convert to uppercase
        logging.debug(f"GuessLetterAction initialized with letter: {self.letter}")


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class HangmanGameState:
    def __init__(self, word_to_guess: str, phase: GamePhase, guesses: List[str], incorrect_guesses: List[str]) -> None:
        self.word_to_guess = word_to_guess.upper()  # Ensure word is uppercase
        self.phase = phase
        self.guesses = guesses
        self.incorrect_guesses = incorrect_guesses

    def is_word_guessed(self) -> bool:
        """ Check if all letters in the word have been guessed """
        return all(letter in self.guesses for letter in self.word_to_guess)

    def has_max_incorrect_guesses(self) -> bool:
        """ Check if max incorrect guesses have been reached """
        return len(self.incorrect_guesses) >= 8


class Hangman:
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
        logging.debug(f"Applying action with letter: {guessed_letter}")
        logging.debug(f"Word to guess: {self._state.word_to_guess}")
        logging.debug(f"Current guesses: {self._state.guesses}")
        logging.debug(f"Incorrect guesses: {self._state.incorrect_guesses}")

        if guessed_letter in self._state.guesses or guessed_letter in self._state.incorrect_guesses:
            logging.debug(f"Letter '{guessed_letter}' has already been guessed.")
            return

        if guessed_letter in self._state.word_to_guess:
            logging.debug(f"Letter '{guessed_letter}' is in the word.")
            self._state.guesses.append(guessed_letter)
        else:
            logging.debug(f"Letter '{guessed_letter}' is not in the word.")
            self._state.incorrect_guesses.append(guessed_letter)

        # Check for game end conditions
        if self._state.is_word_guessed():
            logging.debug("The word has been guessed. Ending the game.")
            self._state.phase = GamePhase.FINISHED
        elif self._state.has_max_incorrect_guesses():
            logging.debug("Maximum incorrect guesses reached. Ending the game.")
            self._state.phase = GamePhase.FINISHED

    def get_player_view(self, idx_player: int) -> HangmanGameState:
        """ Return the game state as seen by the player """
        return self.get_state()


class RandomPlayer:
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
