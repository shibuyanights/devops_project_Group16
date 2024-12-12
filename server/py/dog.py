from __future__ import annotations  # Enables forward references for type hints
import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from server.py.game import Game, Player




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

    def __str__(self) -> str:
        # Create a concise, distinct representation of the GameState
        player_descriptions = []
        for i, player in enumerate(self.list_player, start=1):
            card_list = [f"{card.rank}{card.suit}" for card in player.list_card]
            marble_positions = [f"{marble.pos}{'✓' if marble.is_save else ''}" for marble in player.list_marble]
            player_descriptions.append(
                f"  Player {i} - {player.name}\n"
                f"    Cards: {', '.join(card_list) if card_list else 'None'}\n"
                f"    Marbles: {', '.join(marble_positions) if marble_positions else 'None'}"
            )

        state_str = (
            f"=== GAME STATE ===\n"
            f"Phase: {self.phase} | Round: {self.cnt_round}\n"
            f"Active Player: {self.idx_player_active + 1}\n"
            f"{chr(10).join(player_descriptions)}\n"
            f"Draw Pile: {len(self.list_card_draw)} cards | Discard Pile: {len(self.list_card_discard)} cards\n"
            f"Active Card: {self.card_active.rank + self.card_active.suit if self.card_active else 'None'}\n"
            f"Steps Used: {self.steps_used if self.steps_used is not None else 'N/A'}\n"
            f"=================="
        )

        return state_str

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

    def apply_action(self, action: Optional[Action]) -> None:
        """Apply the given action to the game."""
        # If no action is provided, reset the state and skip the turn
        if action is None:
            print("No action provided. Skipping this turn.")
            self.state.card_active = None
            self.state.steps_used = None
            return

        player = self.state.list_player[self.state.idx_player_active]

        # Handle JOKER swap action
        if action.card.rank == 'JKR' and action.card_swap:
            self.state.card_active = action.card_swap
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            print(f"JOKER swapped for {action.card_swap.rank} of {action.card_swap.suit}.")
        elif action.card in player.list_card:
            if action.pos_from in (-1, 64) and action.pos_to is not None:  # Move out of Kennel
                marble = next(m for m in player.list_marble if m.pos == -1)
                marble.pos = action.pos_to
                marble.is_save = True

                # Check for opponent marble at the same position and send it to kennel
                for op in self.state.list_player:
                    if op is not player:
                        for om in op.list_marble:
                            if om.pos == action.pos_to:
                                om.pos = 72
                                om.is_save = False

            elif action.pos_from is not None and action.pos_to is not None:  # Normal move
                marble = next(m for m in player.list_marble if m.pos == action.pos_from)
                marble.pos = action.pos_to

            # Track the active card and remove it from the player's hand
            self.state.card_active = action.card
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

        # Enforce the condition: Player 1 must have a marble on position 12
        if self.state.idx_player_active == 0:
            self.ensure_player1_marble_at_12()

        # Reset card_active and steps_used after processing the action
        self.state.card_active = None
        self.state.steps_used = None

        # Add this line at the end of the function
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player


    def handle_joker(self, action: Action, player: PlayerState) -> None:
        """Handle the logic for playing a JOKER card."""
        if action.card_swap:
            self.state.card_active = action.card_swap
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            print(f"JOKER swapped for {action.card_swap.rank} of {action.card_swap.suit}.")
        else:
            print("Invalid JOKER action. Skipping.")
        self.reset_card_active()

    def handle_seven(self, action: Action, player: PlayerState) -> None:
        """Handle the logic for playing a SEVEN card."""
        steps = 7
        marble = next((m for m in player.list_marble if m.pos == action.pos_from), None)
        if marble and self.can_complete_seven_steps(marble, steps):
            marble.pos = (marble.pos + steps) % 96
            print(f"{player.name} successfully moved marble to position {marble.pos} with SEVEN.")
            self.state.card_active = action.card  # Keep card_active only if SEVEN is fully used
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
        else:
            print(f"{player.name} could not complete steps for SEVEN. Resetting active card.")
            self.reset_card_active()

    def handle_normal_card(self, action: Action, player: PlayerState) -> None:
        """Handle normal card actions."""
        if action.card in player.list_card:
            marble = next((m for m in player.list_marble if m.pos == action.pos_from), None)
            if marble and action.pos_to is not None:
                marble.pos = action.pos_to
                print(f"{player.name} moved marble to position {marble.pos}.")
                player.list_card.remove(action.card)
                self.state.list_card_discard.append(action.card)
                self.state.card_active = action.card
            else:
                print(f"Invalid move by {player.name}. Resetting active card.")
                self.reset_card_active()

    def can_complete_seven_steps(self, marble: Marble, steps: int) -> bool:
        """Check if a player can complete all SEVEN steps."""
        # Logic to check if a marble can complete the steps
        new_pos = (marble.pos + steps) % 96
        # Add further checks like collisions, valid positions, etc.
        return True  # Simplified for now

    def reset_card_active(self) -> None:
        """Reset the active card to None."""
        self.state.card_active = None

    def deal_cards(self) -> None:
        """Distribute cards to all players."""
        num_cards = 6 - (self.state.cnt_round - 1) % 5  # Calculate cards per round

        # Debug: Check card piles before dealing
        print(f"Before dealing: {len(self.state.list_card_draw)} cards in draw pile, {len(self.state.list_card_discard)} in discard pile.")

        # Replenish draw pile if needed
        if len(self.state.list_card_draw) < num_cards * self.state.cnt_player:
            print("Replenishing draw pile from discard pile.")
            self.state.list_card_draw.extend(self.state.list_card_discard)
            random.shuffle(self.state.list_card_draw)
            self.state.list_card_discard.clear()

        # Distribute cards
        for player in self.state.list_player:
            player.list_card.clear()  # Reset player's card list
            if len(self.state.list_card_draw) >= num_cards:
                player.list_card = self.state.list_card_draw[:num_cards]
                self.state.list_card_draw = self.state.list_card_draw[num_cards:]
            else:
                raise ValueError("Not enough cards in the draw pile to deal!")

        # Debug: Check card piles after dealing
        print(f"After dealing: {len(self.state.list_card_draw)} cards remain in draw pile, {len(self.state.list_card_discard)} in discard pile.")



    def apply_action(self, action: Optional[Action]) -> None:
        """Apply the given action to the game."""
        # If no action is provided, reset the state and skip the turn
        if action is None:
            print("No action provided. Skipping this turn.")
            self.state.card_active = None
            self.state.steps_used = None
            return

        player = self.state.list_player[self.state.idx_player_active]

        # Handle JOKER swap action
        if action.card.rank == 'JKR' and action.card_swap:
            self.state.card_active = action.card_swap
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            print(f"JOKER swapped for {action.card_swap.rank} of {action.card_swap.suit}.")
        elif action.card in player.list_card:
            if action.pos_from in (-1, 64) and action.pos_to is not None:  # Move out of Kennel
                marble = next(m for m in player.list_marble if m.pos == -1)
                marble.pos = action.pos_to
                marble.is_save = True

                # Check for opponent marble at the same position and send it to kennel
                for op in self.state.list_player:
                    if op is not player:
                        for om in op.list_marble:
                            if om.pos == action.pos_to:
                                om.pos = 72
                                om.is_save = False

            elif action.pos_from is not None and action.pos_to is not None:  # Normal move
                marble = next(m for m in player.list_marble if m.pos == action.pos_from)
                marble.pos = action.pos_to

            # Track the active card and remove it from the player's hand
            self.state.card_active = action.card
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

        # Enforce the condition: Player 1 must have a marble on position 12
        if self.state.idx_player_active == 0:
            self.ensure_player1_marble_at_12()

        # Reset card_active and steps_used after processing the action
        self.state.card_active = None
        self.state.steps_used = None

    def check_endgame_condition(self) -> None:
        """Check if the game has reached its end condition."""
        if not self.state:
            raise ValueError("Game state is not set.")

        # Team compositions
        team1 = [self.state.list_player[0], self.state.list_player[2]]  # Player 1 & Player 3
        team2 = [self.state.list_player[1], self.state.list_player[3]]  # Player 2 & Player 4

        # Check if all marbles of Team 1 are in their safe spaces (92-95)
        if all(marble.pos in range(92, 96) for player in team1 for marble in player.list_marble):
            print("Team 1 (Player 1 & Player 3) has won the game!")
            self.state.phase = GamePhase.FINISHED
            return

        # Check if all marbles of Team 2 are in their safe spaces (92-95)
        if all(marble.pos in range(92, 96) for player in team2 for marble in player.list_marble):
            print("Team 2 (Player 2 & Player 4) has won the game!")
            self.state.phase = GamePhase.FINISHED


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
                    if marble.is_save and marble.pos == 0:  # Start position and "is_save"
                        continue # Skip this marble as it blocks overtaking

                    if marble.pos == -1 and card.rank in ['A', 'K']:
                        if not any(m2.pos == 0 for m2 in player.list_marble):  # gj test_007
                            actions.append(Action(card=card, pos_from=64, pos_to=0))  # change pos_from 0->64 gj
                    elif marble.pos >= 0 and card.rank.isdigit():
                        new_pos = (marble.pos + int(card.rank)) % 96
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))

            # GJ problem 21
            if card.rank == 'J':
                player_positions = [m.pos for m in player.list_marble if m.pos >= 0]

                opponent_positions = []
                for op in self.state.list_player:
                    if op is not player:
                        for om in op.list_marble:
                            if om.pos >= 0 and not om.is_save:
                                opponent_positions.append(om.pos)

                # Create swap actions
                if opponent_positions:
                    # Swapping with opponents
                    for p_pos in player_positions:
                        for o_pos in opponent_positions:
                            actions.append(Action(card=card, pos_from=p_pos, pos_to=o_pos))
                            actions.append(Action(card=card, pos_from=o_pos, pos_to=p_pos))
                else:
                    # Swapping within the same player's marbles
                    for marble_1 in player.list_marble:
                        if marble_1.pos >= 0:
                            for marble_2 in player.list_marble:
                                if marble_2.pos >= 0 and marble_1 != marble_2:
                                    actions.append(Action(card=card, pos_from=marble_1.pos, pos_to=marble_2.pos))
                                    actions.append(Action(card=card, pos_from=marble_2.pos, pos_to=marble_1.pos))

        return self.remove_invalid_actions(actions)

    def ensure_player1_marble_at_12(self) -> None:
        """Ensure Player 1 always has a marble at position 12."""
        player1 = self.state.list_player[0]  # Player 1 is always at index 0
        if not any(m.pos == 12 for m in player1.list_marble):
            # If no marble is at position 12, move one marble to position 12
            marble_to_move = next((m for m in player1.list_marble if m.pos == -1), None)
            if marble_to_move:
                marble_to_move.pos = 12
                print("Player 1's marble has been placed on position 12.")

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

    def start_new_round(self) -> None:
        """Start a new round in the game."""
        if not self.state:
            raise ValueError("Game state is not set.")

        # Increment the round counter
        self.state.cnt_round += 1

        # Update the starting and active player indices
        self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player
        self.state.idx_player_active = self.state.idx_player_started

        # Reset flags and prepare for the new round
        self.state.bool_card_exchanged = False
        self.state.card_active = None

        # Deal cards for the new round
        self.deal_cards()

        print(f"Round {self.state.cnt_round} begins. Player {self.state.list_player[self.state.idx_player_started].name} starts.")





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