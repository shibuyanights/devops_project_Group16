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


class Marble(BaseModel):
    pos: int       # position on board (-1 for Kennel, 0 to 95 for board positions)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str                  # name of player
    list_card: List[Card]      # list of cards
    list_marble: List[Marble]  # list of marbles


class Action(BaseModel):
    card: Card                 # card to play
    pos_from: Optional[int]    # position to move the marble from
    pos_to: Optional[int]      # position to move the marble to
    card_swap: Optional[Card] = None  # Default value of None for optional field


class GamePhase(str, Enum):
    SETUP = 'setup'            # before the game has started
    RUNNING = 'running'        # while the game is running
    FINISHED = 'finished'      # when the game is finished


class GameState(BaseModel):
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit=suit, rank=rank)
        for suit in LIST_SUIT for rank in LIST_RANK[:-1]
    ] * 2 + [Card(suit='', rank='JKR')] * 6  # Full deck

    cnt_player: int = 4                # number of players (must be 4)
    phase: GamePhase = GamePhase.SETUP # current phase of the game
    cnt_round: int = 1                 # current round
    bool_game_finished: bool = False  # true if game has finished
    bool_card_exchanged: bool = False # true if cards were exchanged in the round
    idx_player_started: int = 0       # index of player that started the round
    idx_player_active: int = 0        # index of active player in round
    list_player: List[PlayerState] = []  # Initialize as an empty list
    list_card_draw: List[Card] = []   # Renamed from list_id_card_draw
    list_card_discard: List[Card] = []  # Matches the test requirements
    card_active: Optional[Card] = None  # active card


class Dog(Game):
    def __init__(self) -> None:
        # Initialize the game state with default values
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

        # Deal cards to all players
        self.deal_cards()

        # Update phase to RUNNING after all initialization
        self.state.phase = GamePhase.RUNNING

    def deal_cards(self) -> None:
        """
        Distribute cards to all players.
        """
        num_cards = 6 - (self.state.cnt_round - 1) % 5  # Calculate the number of cards to deal
        print(f"Dealing {num_cards} cards to each player in round {self.state.cnt_round}.")

        # Replenish draw pile if needed
        if len(self.state.list_card_draw) < num_cards * self.state.cnt_player:
            print("Replenishing draw pile from discard pile.")
            self.state.list_card_draw.extend(self.state.list_card_discard)
            random.shuffle(self.state.list_card_draw)
            self.state.list_card_discard.clear()

        # Distribute cards to players
        for i, player in enumerate(self.state.list_player):
            player.list_card.clear()  # Clear the player's card list to reset
            if len(self.state.list_card_draw) >= num_cards:
                player.list_card = self.state.list_card_draw[:num_cards]
                self.state.list_card_draw = self.state.list_card_draw[num_cards:]
                print(f"Player {i+1} received cards: {[card.rank for card in player.list_card]}")
            else:
                raise ValueError("Not enough cards in the draw pile to deal!")

        print(f"After dealing: {len(self.state.list_card_draw)} cards remain in the draw pile.")
        print(f"Discard pile size: {len(self.state.list_card_discard)}")

    def start_new_round(self) -> None:
        """
        Start a new round and deal cards again.
        """
        if self.state.bool_game_finished:
            raise ValueError("Cannot start a new round; the game is already finished.")

        self.state.cnt_round += 1  # Increment the round
        self.state.bool_card_exchanged = False  # Reset card exchange status
        self.state.idx_player_active = self.state.idx_player_started  # Reset active player index

        print(f"Starting round {self.state.cnt_round}...")
        self.deal_cards()  # Deal cards for the new round

        # Verify that all players have the correct number of cards
        expected_cards = 6 - (self.state.cnt_round - 1) % 5
        for i, player in enumerate(self.state.list_player):
            if len(player.list_card) != expected_cards:
                print(f"Error: Player {i+1} has {len(player.list_card)} cards, expected {expected_cards}.")
                raise AssertionError(
                    f"Player {i+1} has {len(player.list_card)} cards, expected {expected_cards}."
                )

    def apply_action(self, action: Optional[Action]) -> None:
        """ Apply the given action to the game """
        if action is None:
            print("No action provided. Skipping this turn.")
            return

        player = self.state.list_player[self.state.idx_player_active]

        if action.card in player.list_card:
            if action.pos_from == -1 and action.pos_to is not None:  # -1 for Kennel
                marble = next(m for m in player.list_marble if m.pos == -1)
                marble.pos = action.pos_to
                marble.is_save = True
            elif action.pos_from is not None and action.pos_to is not None:
                marble = next(m for m in player.list_marble if m.pos == action.pos_from)
                marble.pos = action.pos_to
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

    def get_list_action(self) -> List[Action]:
        """ Get a list of possible actions for the active player """
        player = self.state.list_player[self.state.idx_player_active]
        actions = []
        for card in player.list_card:
            for marble in player.list_marble:
                if marble.pos == -1 and card.rank in ['A', 'K', 'JKR']:  # -1 for Kennel
                    actions.append(Action(card=card, pos_from=-1, pos_to=0))
                elif marble.pos >= 0:  # On the board
                    pos = marble.pos
                    if card.rank.isdigit():
                        new_pos = (pos + int(card.rank)) % 96
                        actions.append(Action(card=card, pos_from=pos, pos_to=new_pos))

        return actions

    def get_player_view(self, idx_player: int) -> GameState:
        """ Get the masked state for the active player """
        return self.state

    def set_state(self, state: GameState) -> None:
        """ Set the game to a given state """
        self.state = state

    def get_state(self) -> GameState:
        """ Get the complete, unmasked game state """
        return self.state

    def print_state(self) -> None:
        """ Print the current game state """
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
