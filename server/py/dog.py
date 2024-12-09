from __future__ import annotations  # Enables forward references for type hints
from server.py.game import Game, Player
from typing import List, Optional, ClassVar
from pydantic import BaseModel
import random
from enum import Enum



# Constants moved outside the class for clarity and reuse
LIST_SUIT = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
LIST_RANK = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A', 'JKR']



class Card(BaseModel):
    suit: str  # card suit (color)
    rank: str  # card rank

    def __lt__(self, other: Card) -> bool:
        """Implement comparison for sorting: first by suit, then by rank."""
        return self.suit < other.suit or (
            self.suit == other.suit and LIST_RANK.index(self.rank) < LIST_RANK.index(other.rank)
        )

    def __eq__(self, other: Card) -> bool:
        """Equality comparison for Card objects."""
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self) -> int:
        """Make Card hashable."""
        return hash((self.suit, self.rank))






class Marble(BaseModel):
    pos: int       # position on board (-1 for Kennel, 0 to 95 for board positions)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card
    pos_from: Optional[int] = None
    pos_to: Optional[int] = None
    card_swap: Optional[Card] = None

    def __hash__(self):
        """Make Action hashable."""
        return hash((self.card, self.pos_from, self.pos_to, self.card_swap))

    def __eq__(self, other):
        """Define equality for Action."""
        if not isinstance(other, Action):
            return False
        return (
            self.card == other.card
            and self.pos_from == other.pos_from
            and self.pos_to == other.pos_to
            and self.card_swap == other.card_swap
        )



class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit=suit, rank=rank)
        for suit in LIST_SUIT for rank in LIST_RANK[:-1]
    ] * 2 + [Card(suit='', rank='JKR')] * 6  # Full deck

    cnt_player: int = 4
    phase: GamePhase = GamePhase.SETUP
    cnt_round: int = 1
    bool_game_finished: bool = False
    bool_card_exchanged: bool = False
    idx_player_started: int = 0
    idx_player_active: int = 0
    list_player: List[PlayerState] = []
    list_card_draw: List[Card] = []
    list_card_discard: List[Card] = []
    card_active: Optional[Card] = None

    # Add steps_used attribute
    steps_used: Optional[int] = None

class Dog(Game):
    def __init__(self) -> None:
        """Initialize the game with default values."""
        # Initialize the game state
        self.state = GameState(
            list_player=[
                PlayerState(
                    name=f"Player {i+1}",
                    list_card=[],
                    list_marble=[Marble(pos=-1, is_save=False) for _ in range(4)]  # -1 for Kennel
                ) for i in range(4)
            ],
            list_card_draw=random.sample(GameState.LIST_CARD, len(GameState.LIST_CARD)),
            list_card_discard=[],
        )

        # Assign the starting player
        self.state.idx_player_started = random.randint(0, self.state.cnt_player - 1)
        self.state.idx_player_active = self.state.idx_player_started

        # Deal cards to players
        self.deal_cards()

        # Update phase to RUNNING
        self.state.phase = GamePhase.RUNNING

    def deal_cards(self) -> None:
        """Distribute cards to all players."""
        num_cards = 6 - (self.state.cnt_round - 1) % 5  # Calculate cards per round
        print(f"Dealing {num_cards} cards to each player in round {self.state.cnt_round}.")

        # Replenish draw pile if needed
        if len(self.state.list_card_draw) < num_cards * self.state.cnt_player:
            print("Replenishing draw pile from discard pile.")
            self.state.list_card_draw.extend(self.state.list_card_discard)
            random.shuffle(self.state.list_card_draw)
            self.state.list_card_discard.clear()

        # Distribute cards
        for i, player in enumerate(self.state.list_player):
            player.list_card.clear()  # Reset player's card list
            if len(self.state.list_card_draw) >= num_cards:
                player.list_card = self.state.list_card_draw[:num_cards]
                self.state.list_card_draw = self.state.list_card_draw[num_cards:]
                print(f"Player {i+1} received cards: {[card.rank for card in player.list_card]}")
            else:
                raise ValueError("Not enough cards in the draw pile to deal!")

        print(f"After dealing: {len(self.state.list_card_draw)} cards remain in the draw pile.")
        print(f"Discard pile size: {len(self.state.list_card_discard)}")

    def apply_action(self, action: Optional[Action]) -> None:
        """Apply the given action to the game."""
        if action is None:
            print("No action provided. Skipping this turn.")
            return

        player = self.state.list_player[self.state.idx_player_active]

        # Handle JOKER swap action
        if action.card.rank == 'JKR' and action.card_swap:
            self.state.card_active = action.card_swap
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            print(f"JOKER swapped for {action.card_swap.rank} of {action.card_swap.suit}.")
            return

        # Handle other actions
        if action.card in player.list_card:
            if action.pos_from in(-1,64) and action.pos_to is not None:  # Move out of Kennel #change gj -1-> (-1,64)
                marble = next(m for m in player.list_marble if m.pos == -1)
                marble.pos = action.pos_to
                marble.is_save = True
                # GJ Check for opponent marble at the same position and send it to kennel (pos=72)
                for op in self.state.list_player:
                    if op is not player:
                        for om in op.list_marble:
                            if om.pos == action.pos_to:
                                om.pos = 72
                                om.is_save = False
            elif action.pos_from is not None and action.pos_to is not None:  # Normal move
                marble = next(m for m in player.list_marble if m.pos == action.pos_from)
                marble.pos = action.pos_to
            self.state.card_active = action.card
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player."""
        player = self.state.list_player[self.state.idx_player_active]
        actions: List[Action] = []

        for card in player.list_card:
            if card.rank == 'JKR':
                actions.append(Action(card=card, pos_from=64, pos_to=0))
                if self.state.cnt_round == 0:
                    for suit in LIST_SUIT:
                        actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='A')))
                        actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='K')))
                else:
                    for suit in LIST_SUIT:
                        for rank in LIST_RANK[:-1]:  # Exclude 'JKR'
                            actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank=rank)))
            else:
                for marble in player.list_marble:
                    if marble.pos == -1 and card.rank in ['A', 'K']:
                        if not any(m2.pos == 0 for m2 in player.list_marble): #gj test_007
                            actions.append(Action(card=card, pos_from=64, pos_to=0))  #change pos_from 0->64 gj
                    elif marble.pos >= 0 and card.rank.isdigit():
                        new_pos = (marble.pos + int(card.rank)) % 96
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))

        return self.remove_invalid_actions(actions)

    def remove_invalid_actions(self, actions: List[Action]) -> List[Action]:
        """Remove duplicate or invalid actions."""
        return list(set(actions))

    def get_player_view(self, idx_player: int) -> GameState:
        """Get a masked view of the game state for the given player."""
        return self.state

    def set_state(self, state: GameState) -> None:
        """Set the game to a given state."""
        self.state = state

    def get_state(self) -> GameState:
        """Get the complete, unmasked game state."""
        return self.state

    def print_state(self) -> None:
        """Print the current game state."""
        print(f"Phase: {self.state.phase}")
        print(f"Round: {self.state.cnt_round}")
        for player in self.state.list_player:
            print(f"{player.name}:")
            print(f"  Cards: {[card.rank for card in player.list_card]}")
            print(f"  Marbles: {[marble.pos for marble in player.list_marble]}")


class RandomPlayer(Player):
    def select_action(self, state: GameState, actions: List[Action]) -> Action:
        """ Given masked game state and possible actions, select the next action """
        if actions:
            return random.choice(actions)
        raise ValueError("No valid actions available")


if __name__ == '__main__':
    game = Dog()
    game.start_new_round()  # Start a new round for testing
    game.print_state()