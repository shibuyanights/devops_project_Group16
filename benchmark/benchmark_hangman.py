import sys
import string
from benchmark import Benchmark
from server.py.hangman import HangmanGameState, GamePhase, GuessLetterAction


class HangmanBenchmark(Benchmark):

    def test_set_state_method(self):
        """Test 001: Set/get methods work properly [1 point]"""
        self.game_server.reset()
        state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
        self.game_server.set_state(state)
        game_state = self.game_server.get_state()
        assert state == game_state, "Applying 'set_state' and then 'get_state' returns a different state"

    def test_action_list(self):
        """Test 002: Action list contains only 'unused' capital letters [1 point]"""
        self.game_server.reset()
        state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
        self.game_server.set_state(state)

        # initial actions
        actions = self.game_server.get_list_action()
        hint = "Initial actions list should contain all existing capital letters"
        assert {action.letter for action in actions} == set(string.ascii_uppercase), hint

        # testcase 1
        test_state1 = HangmanGameState(word_to_guess="", guesses=['A','B','C'], phase=GamePhase.RUNNING)
        self.game_server.set_state(test_state1)
        actions1 = self.game_server.get_list_action()
        hint = "Some 'guessed' letters are still in the action list"
        assert {action.letter for action in actions1} == set(string.ascii_uppercase[3:]), hint

        # testcase 2
        test_state2 = HangmanGameState(word_to_guess="", guesses=[*string.ascii_uppercase], phase=GamePhase.RUNNING)
        self.game_server.set_state(test_state2)
        actions2 = self.game_server.get_list_action()
        assert len(actions2) == 0, "Having guessed all letters, the action list should be empty"

    def test_apply_action_general(self):
        """Test 003: Apply action method adds new guess to gamestate [1 point]"""
        self.game_server.reset()
        state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
        self.game_server.set_state(state)
        self.game_server.apply_action(GuessLetterAction(letter='D'))
        state = self.game_server.get_state()
        hint = "After applying a 'GuessLetterAction' the letter is not in the list of 'guesses'"
        assert state.guesses == ['D'], hint

    def test_apply_action_lowercase(self):
        """Test 004: Apply action also works for lowercase letters [1 point]"""
        self.game_server.reset()
        state = HangmanGameState(word_to_guess='devops', guesses=[], phase=GamePhase.RUNNING)
        self.game_server.set_state(state)
        self.game_server.apply_action(GuessLetterAction(letter='x'))
        state = self.game_server.get_state()
        assert state.guesses == ['X'], "Guessing a lower case letter doesn't work"

    def test_game_ending(self):
        """Test 005: Game ends with 8 wrong guesses or when secret word is revealed [1 point]"""
        self.game_server.reset()

        # 8 wrong guesses
        test_state1 = HangmanGameState(word_to_guess="XY", guesses=[*'ABCDEFG'], phase=GamePhase.RUNNING)
        self.game_server.set_state(test_state1)
        self.game_server.apply_action(GuessLetterAction(letter='H'))
        hint = "Gamephase should be 'FINISHED' after 8 wrong guesses"
        assert self.game_server.get_state().phase == GamePhase.FINISHED, hint

        # secret word is revealed
        test_state2 = HangmanGameState(word_to_guess="XY", guesses=[*'AX'], phase=GamePhase.RUNNING)
        self.game_server.set_state(test_state2)
        self.game_server.apply_action(GuessLetterAction(letter='Y'))
        hint = "Gamephase should be 'FINISHED' after revealing the secret word"
        assert self.game_server.get_state().phase == GamePhase.FINISHED, hint

    def test_secret_word_lowercase_letters(self):
        """Test 006: Game also works when secret words contain lowercase letters [1 point]"""
        self.game_server.reset()
        test_state1 = HangmanGameState(word_to_guess="Xy", guesses=[*'AY'], phase=GamePhase.RUNNING)
        self.game_server.set_state(test_state1)
        self.game_server.apply_action(GuessLetterAction(letter='x'))
        assert self.game_server.get_state().phase == GamePhase.FINISHED


if __name__ == "__main__":

    benchmark = HangmanBenchmark(sys.argv)
    benchmark.run_tests()
