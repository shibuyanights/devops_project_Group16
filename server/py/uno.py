from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
import random
import copy

# Placeholder for Game and Player classes
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

    def __lt__(self, other):
        # Define a tuple for comparison, ensuring all elements are comparable
        self_tuple = (
            self.card.color if self.card and self.card.color else "",
            self.card.number if self.card and self.card.number is not None else -1,
            self.card.symbol if self.card and self.card.symbol else "",
            self.color if self.color else "",
            self.draw if self.draw is not None else 0,
            self.uno
        )
        other_tuple = (
            other.card.color if other.card and other.card.color else "",
            other.card.number if other.card and other.card.number is not None else -1,
            other.card.symbol if other.card and other.card.symbol else "",
            other.color if other.color else "",
            other.draw if other.draw is not None else 0,
            other.uno
        )
        return self_tuple < other_tuple


class PlayerState(BaseModel):
    name: str = None  # name of player
    list_card: List[Card] = []  # list of cards


class GamePhase(str, Enum):
    SETUP = "setup"  # before the game has started
    RUNNING = "running"  # while the game is running
    FINISHED = "finished"  # when the game is finished


class GameState(BaseModel):
    CNT_HAND_CARDS: int = 7
    LIST_COLOR: List[str] = ["red", "green", "yellow", "blue", "any"]
    LIST_SYMBOL: List[str] = ["skip", "reverse", "draw2", "wild", "wilddraw4"]
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
    missed_uno_penalty: int = 4  # cards drawn for missing UNO call


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

        # Ensure cnt_player matches the number of players in list_player
        if not self.state.list_player:
            for i in range(self.state.cnt_player):
                self.state.list_player.append(
                    PlayerState(name=f"Player {i + 1}", list_card=[])
                )

        if self.state.cnt_player != len(self.state.list_player):
            raise ValueError(
                f"Mismatch between cnt_player ({self.state.cnt_player}) and number of players in list_player ({len(self.state.list_player)})."
            )

        # Ensure the deck has valid cards
        if len(self.state.list_card_draw) < self.state.cnt_player * self.state.CNT_HAND_CARDS + 1:
            raise ValueError("Not enough cards in the draw pile to initialize the game.")

        # Initialize discard pile
        if not self.state.list_card_discard:
            while self.state.list_card_draw:
                card = self.state.list_card_draw.pop()
                if card.symbol not in ["wild", "wilddraw4"]:
                    self.state.list_card_discard.append(card)
                    self.state.color = card.color
                    if card.symbol == "reverse":
                        self.state.direction *= -1
                    elif card.symbol == "skip":
                        self.state.idx_player_active = (
                            (self.state.idx_player_active or 0) + 1
                        ) % self.state.cnt_player
                    elif card.symbol == "draw2":
                        self.state.cnt_to_draw += 2
                    break

        # Fix for wilddraw4 being the first card
        if self.state.list_card_discard and self.state.list_card_discard[-1].symbol == "wilddraw4":
            raise ValueError("First discard card cannot be WILD DRAW 4.")

        # Assign an active player
        if self.state.idx_player_active is None:
            self.state.idx_player_active = random.randint(0, self.state.cnt_player - 1)

        # Adjust for DRAW 2 cards on top
        if self.state.list_card_discard and self.state.list_card_discard[-1].symbol == "draw2":
            self.state.cnt_to_draw = 2

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
            is_valid_color = card.color == self.state.color
            is_valid_number = card.number == top_card.number
            is_valid_symbol = card.symbol == top_card.symbol
            is_wild = card.color == "any"

            if is_valid_color or is_valid_number or is_valid_symbol or is_wild:
                # Special case: wilddraw4 must be played legally
                if card.symbol == "wilddraw4":
                    has_color_match = any(
                        c.color == self.state.color and c.color != "any"
                        for c in active_player.list_card
                    )
                    if has_color_match:
                        continue  # Skip invalid wilddraw4 play
                    # Add actions for each color choice with draw set to 4
                    for color in self.state.LIST_COLOR:
                        if color != "any":
                            actions.append(Action(card=card, color=color, draw=4))
                else:
                    actions.append(Action(card=card, color=card.color if not is_wild else None))

        # Add draw action if no playable cards
        if not actions:
            actions.append(Action(draw=max(1, self.state.cnt_to_draw)))

        return actions







        # Check playable cards
        for card in active_player.list_card:
            if (
                card.color == self.state.color
                or card.number == top_card.number
                or card.symbol == top_card.symbol
                or card.color == "any"
            ):
                # For wilddraw4, check if it can be legally played
                if card.symbol == "wilddraw4" and any(
                    c.color == self.state.color for c in active_player.list_card if c.color != "any"
                ):
                    continue
                actions.append(Action(card=card, color=card.color if card.color != "any" else None))

        # Add draw action if no playable cards
        if not actions:
            actions.append(Action(draw=max(1, self.state.cnt_to_draw)))
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
            self.state.cnt_to_draw = 0

            # Do not switch to the next player after a draw action
            return

        else:
            # Player plays a card
            card = action.card
            self.state.list_player[self.state.idx_player_active].list_card.remove(card)
            self.state.list_card_discard.append(card)
            self.state.color = action.color or card.color

            # Handle special cards
            if card.symbol == "skip":
                self.state.idx_player_active = (
                    self.state.idx_player_active + 2 * self.state.direction
                ) % self.state.cnt_player
            elif card.symbol == "reverse":
                self.state.direction *= -1
            elif card.symbol == "draw2":
                self.state.cnt_to_draw += 2
            elif card.symbol == "wilddraw4":
                self.state.cnt_to_draw += 4

            # Handle UNO penalty
            if len(self.state.list_player[self.state.idx_player_active].list_card) == 1 and not action.uno:
                for _ in range(self.state.missed_uno_penalty):
                    if self.state.list_card_draw:
                        card = self.state.list_card_draw.pop()
                        self.state.list_player[self.state.idx_player_active].list_card.append(card)

        # Check if the game is finished
        if not self.state.list_player[self.state.idx_player_active].list_card:
            self.state.phase = GamePhase.FINISHED
        else:
            # Move to the next player
            self.state.idx_player_active = (
                self.state.idx_player_active + self.state.direction
            ) % self.state.cnt_player




# Main Section
if __name__ == "__main__":
    uno = Uno()

    # Generate a deck with exactly 93 cards
    colors = ["red", "blue", "green", "yellow"]
    numbers = list(range(10))  # Cards numbered 0-9
    special_symbols = ["skip", "reverse", "draw2"]  # Special action cards

    # Create the deck with adjusted rules
    list_card_draw = []

    # Add regular cards (0-9) once per color
    for color in colors:
        for number in numbers:
            list_card_draw.append(Card(color=color, number=number, symbol=None))

    # Add duplicates for numbers 1-5 (to reach 93 cards)
    for color in colors:
        for number in range(1, 6):  # Duplicates for numbers 1-5
            list_card_draw.append(Card(color=color, number=number, symbol=None))

    # Add special cards (2 of each per color)
    for color in colors:
        for symbol in special_symbols:
            list_card_draw.append(Card(color=color, number=None, symbol=symbol))
            list_card_draw.append(Card(color=color, number=None, symbol=symbol))

    # Add wild cards
    wild_cards = ["wild", "wilddraw4"]
    for wild in wild_cards:
        for _ in range(4):  # 4 of each wild card
            list_card_draw.append(Card(color="any", number=None, symbol=wild))

    # Ensure the deck is trimmed to exactly 93 cards
    if len(list_card_draw) > 93:
        list_card_draw = list_card_draw[:93]
    elif len(list_card_draw) < 93:
        # Add one more card to make it exactly 93
        list_card_draw.append(Card(color="red", number=7, symbol=None))  # Example filler card