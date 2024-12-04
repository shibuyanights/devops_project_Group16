from server.models import GameState, PlayerState, Card, Marble, Action
from enum import Enum

class Dog:
    def __init__(self):
        """Initialize the game server."""
        self.state = None
        self.reset()

    def reset(self):
        """Reset the game to its initial state."""
        self.state = GameState()  # Create the game state
        # Initialize game state (players, marbles, cards, etc.)

    def get_state(self):
        """Return the current game state."""
        return self.state

    def set_state(self, state):
        """Set the game state to a new state."""
        self.state = state

    def apply_action(self, action):
        """Apply an action to the game state."""
        # Modify game state based on the action
        pass

    def get_list_action(self):
        """Return all valid actions for the current game state."""
        return []  # Replace with actual logic

