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
        # Safely compare Actions, accounting for None values
        return (
            (self.card.color if self.card else "", 
             self.card.number if self.card else -1, 
             self.card.symbol if self.card else "",
             self.draw or 0, 
             self.uno)
            < (other.card.color if other.card else "", 
               other.card.number if other.card else -1, 
               other.card.symbol if other.card else "",
               other.draw or 0, 
               other.uno)
        )


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

        # Assign an active player
        if self.state.idx_player_active is None:
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
            if (
                card.color == self.state.color
                or card.number == top_card.number
                or card.symbol == top_card.symbol
                or card.color == "any"
            ):
                actions.append(Action(card=card, color=card.color if card.color != "any" else None))

        # Add draw action
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

            # Check for UNO penalty
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

    def get_player_view(self, idx_player: int):
        """Get the masked state for the given player."""
        masked_state = copy.deepcopy(self.state)
        for i, player in enumerate(masked_state.list_player):
            if i != idx_player:
                player.list_card = ["Hidden"] * len(player.list_card)
        return masked_state


# Testing and Initialization
if __name__ == "__main__":
    uno = Uno()
    state = GameState(
        list_card_draw=[Card(color="red", number=i) for i in range(10)],
        list_card_discard=[],
        list_player=[PlayerState(name=f"Player {i}") for i in range(4)],  # 4 players
    )
    uno.set_state(state)
    uno.print_state()
