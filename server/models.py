from enum import Enum
from typing import List, Optional

class GamePhase(Enum):
    RUNNING = "running"
    FINISHED = "finished"

class GameState:
    def __init__(self):
        self.phase = GamePhase.RUNNING
        self.cnt_round = 1
        self.list_card_draw = []  # Draw pile
        self.list_card_discard = []  # Discard pile
        self.list_player = []  # List of players (PlayerState)
        self.idx_player_active = 0  # Index of the active player
        self.idx_player_started = 0  # Index of the starting player
        self.card_active = None  # Current active card
        self.bool_card_exchanged = False

class PlayerState:
    def __init__(self, idx_player):
        self.idx_player = idx_player
        self.list_card = []  # Cards in the player's hand
        self.list_marble = []  # Marbles owned by the player

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit  # Suit of the card (♠, ♦, ♥, ♣)
        self.rank = rank  # Rank of the card (A, 2, J, etc.)

class Marble:
    def __init__(self, pos: int, is_save: bool = False):
        self.pos = pos  # Current position
        self.is_save = is_save  # True if in a safe zone

class Action:
    def __init__(self, card: Card, pos_from: int, pos_to: int, card_swap: Optional[Card] = None):
        self.card = card  # The card used for the action
        self.pos_from = pos_from  # Starting position
        self.pos_to = pos_to  # Ending position
        self.card_swap = card_swap  # Optional: For swap actions

