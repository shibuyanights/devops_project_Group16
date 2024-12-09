from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random
import copy

# Define placeholders for Game and Player if not provided
class Game:
    pass


class Player:
    pass


class Card(BaseModel):
    color: Optional[str]  # color of the card (see LIST_COLOR)
    number: Optional[int]  # number of the card (if not a symbol card)
    symbol: Optional[str]  # special cards (see LIST_SYMBOL)


class Action(BaseModel):
    card: Optional[Card] = None  # the card to play
    color: Optional[str] = None  # the chosen color to play (for wild cards)
    draw: Optional[int] = None  # the number of cards to draw for the next player
    uno: bool = False  # true to announce "UNO" with the second last card


class PlayerState(BaseModel):
    name: str = None  # name of player
    list_card: List[Card] = []  # list of cards


class GamePhase(str, Enum):
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class GameState(BaseModel):
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ['red', 'green', 'yellow', 'blue', 'any']
    LIST_SYMBOL: List[str] = ['skip', 'reverse', 'draw2', 'wild', 'wilddraw4']
    list_card_draw: List[Card] = []  # list of cards to draw
    list_card_discard: List[Card] = []  # list of cards discarded
    list_player: List[PlayerState] = []  # list of player-states
    phase: GamePhase = GamePhase.SETUP
    cnt_player: int = 0  # number of players
    idx_player_active: Optional[int] = None  # index of the active player
    direction: int = 1  # direction of play
    color: str = None  # active color
    cnt_to_draw: int = 0  # accumulated cards to draw
    has_drawn: bool = False  # if the current player has drawn a card

class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        """Select an action randomly from the list of available actions."""
        if not actions:
            return None
        return random.choice(actions)


class Uno(Game):

    def __init__(self):
        self.state = None

    def set_state(self, state: GameState):
        """Set the game to a given state."""
        self.state = state
        if not self.state.list_card_discard:
            # Initialize the discard pile with the first valid card
            while self.state.list_card_draw:
                card = self.state.list_card_draw.pop()
                if card.symbol not in ['wild', 'wilddraw4']:
                    self.state.list_card_discard.append(card)
                    self.state.color = card.color
                    break
        self.state.idx_player_active = random.randint(0, self.state.cnt_player - 1)

    def get_state(self):
        """Get the complete, unmasked game state."""
        return self.state

    def print_state(self):
        """Print the current game state."""
        print(f"Active Color: {self.state.color}")
        print(f"Active Player: Player {self.state.idx_player_active + 1}")
        print(f"Discard Pile: {self.state.list_card_discard[-1]}")
        print(f"Direction: {'Clockwise' if self.state.direction == 1 else 'Counterclockwise'}")
        for i, player in enumerate(self.state.list_player):
            print(f"Player {i + 1}: {len(player.list_card)} cards")
        print(f"Draw Pile: {len(self.state.list_card_draw)} cards")

    def get_list_action(self):
        """Get a list of possible actions for the active player."""
        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]
        top_card = self.state.list_card_discard[-1]

        # Check playable cards
        for card in active_player.list_card:
            if card.color == self.state.color or card.number == top_card.number or card.symbol == top_card.symbol or card.color == 'any':
                actions.append(Action(card=card, color=card.color if card.color != 'any' else None))

        # Add draw action
        if not actions:
            actions.append(Action(draw=1))

        return actions

    def apply_action(self, action: Action):
        """Apply the given action to the game."""
        if action.draw:
            # Player draws cards
            for _ in range(action.draw):
                if self.state.list_card_draw:
                    card = self.state.list_card_draw.pop()
                    self.state.list_player[self.state.idx_player_active].list_card.append(card)
            self.state.has_drawn = True
        else:
            # Player plays a card
            card = action.card
            self.state.list_player[self.state.idx_player_active].list_card.remove(card)
            self.state.list_card_discard.append(card)
            self.state.color = action.color or card.color

            # Handle special cards
            if card.symbol == 'skip':
                self.state.idx_player_active = (self.state.idx_player_active + 2 * self.state.direction) % self.state.cnt_player
            elif card.symbol == 'reverse':
                self.state.direction *= -1
            elif card.symbol == 'draw2':
                self.state.cnt_to_draw += 2
            elif card.symbol == 'wilddraw4':
                self.state.cnt_to_draw += 4

        # Check if the game is finished
        if not self.state.list_player[self.state.idx_player_active].list_card:
            self.state.phase = GamePhase.FINISHED
        else:
            # Move to the next player
            self.state.idx_player_active = (self.state.idx_player_active + self.state.direction) % self.state.cnt_player

    def get_player_view(self, idx_player: int):
        """Get the masked state for the given player."""
        masked_state = copy.deepcopy(self.state)
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = ['Hidden'] * len(player.list_card)
        return masked_state
