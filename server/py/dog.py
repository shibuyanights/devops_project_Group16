from __future__ import annotations  # Enables forward references for type hints
import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from server.py.game import Game, Player


class Card(BaseModel):
    suit: str
    rank: str

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        # Convert to strings for comparison
        return str(self) < str(other)

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __str__(self):
        return f"{self.suit}{self.rank}"
    
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
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',      # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        # 2: Move 2 spots forward
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        # 3: Move 3 spots forward
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        # 4: Move 4 spots forward or back
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        # 5: Move 5 spots forward
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        # 6: Move 6 spots forward
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        # 7: Move 7 single steps forward
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        # 8: Move 8 spots forward
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        # 9: Move 9 spots forward
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        # 10: Move 10 spots forward
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'), Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        # Jake: A marble must be exchanged
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        # Queen: Move 12 spots forward
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        # King: Start or move 13 spots forward
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        # Ass: Start or move 1 or 11 spots forward
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
        # Joker: Use as any other card you want
        Card(suit='', rank='JKR'), Card(suit='', rank='JKR'), Card(suit='', rank='JKR')
    ] * 2

    cnt_player: int = 4
    phase: GamePhase
    cnt_round: int
    bool_card_exchanged: bool
    idx_player_started: int
    idx_player_active: int
    list_player: List[PlayerState]
    list_card_draw: List[Card]
    list_card_discard: List[Card]
    card_active: Optional[Card]


class Dog(Game):
    """Dog game implementation"""

    # Define KENNEL_POSITIONS
    KENNEL_POSITIONS = {
        0: [64, 65, 66, 67],  # Blue
        1: [72, 73, 74, 75],  # Green
        2: [80, 81, 82, 83],  # Red
        3: [88, 89, 90, 91],  # Yellow
    }


    # Define FINISH_POSITIONS
    FINISH_POSITIONS = {
        0: [68, 69, 70, 71],  # Blue
        1: [76, 77, 78, 79],  # Green
        2: [84, 85, 86, 87],  # Red
        3: [92, 93, 94, 95],  # Yellow
    }


    # Define START_POSITIONS
    START_POSITIONS = {
        0: 0,    # Blue starts at position 0
        1: 16,   # Green starts at position 16
        2: 32,   # Red starts at position 32
        3: 48,   # Yellow starts at position 48
    }







    def __init__(self) -> None:
        """Initialize the game with default values."""
        self.state = GameState(  # type: ignore #type:unused-ignore
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=[
                PlayerState(
                    name=f"Player {i + 1}",
                    list_card=[],
                    list_marble=[
                        Marble(pos=-1, is_save=False) for _ in range(4)  # Initialize 4 marbles in the "kennel"
                    ]
                ) for i in range(4)
            ],
            list_card_draw=GameState.LIST_CARD.copy(),
            list_card_discard=[],
            card_active=None
        )

        # Assign the starting player
        self.state.idx_player_started = random.randint(0, self.state.cnt_player - 1)
        self.state.idx_player_active = self.state.idx_player_started

        # Initialize steps_used as an attribute of Dog
        self.steps_used = None

        # Deal cards to players
        self.deal_cards()

        # Update phase to RUNNING
        self.state.phase = GamePhase.RUNNING

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

    def _check_if_save_marble_between_current_and_destination(self, current_position: int, destination: int) -> bool:
        """
        Check if a marble with is_save=True is blocking the path between the current position and the destination.

        Args:
            current_position (int): The current position of the marble.
            destination (int): The intended destination position of the marble.

        Returns:
            bool: True if a blocking marble is found; False otherwise.
        """
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.is_save and marble.pos != -1:  # Only consider marbles in valid positions and marked as "safe"
                    if current_position < destination:  # Normal forward move
                        if current_position < marble.pos <= destination:
                            return True
                    else:  # Circular move across position 0
                        if marble.pos > current_position or marble.pos <= destination:
                            return True
        return False




    def create_card_swap_moves(self, player: PlayerState) -> List[Action]:
        """Create actions for exchanging cards."""
        unique_cards = {card.rank + card.suit: card for card in player.list_card}.values()
        return [Action(card=card) for card in unique_cards]

    def process_card_exchange(self, player: PlayerState, action: Action) -> None:
        """Handle the card exchange logic."""
        exchange_partner_index = (self.state.idx_player_active + 2) % self.state.cnt_player
        exchange_partner = self.state.list_player[exchange_partner_index]

        if action and action.card in player.list_card:
            player.list_card.remove(action.card)
            exchange_partner.list_card.append(action.card)

        # Move to the next player after exchanging cards
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.bool_card_exchanged = True

    def create_moves_from_kennel(self, player: PlayerState) -> List[Action]:
        """Create actions for moving marbles out of the kennel."""
        player_index = self.state.list_player.index(player)
        start_position = Dog.STARTING_POSITIONS[player_index]  # Use fixed starting positions
        kennel_moves = []

        for card in player.list_card:
            if card.rank in ["A", "K", "JKR"]:  # Only these cards can start marbles
                for marble in player.list_marble:
                    if marble.pos == -1:  # Marble is still in the kennel
                        kennel_moves.append(Action(card=card, pos_from=-1, pos_to=start_position))
        return kennel_moves


    def generate_joker_options(self, player: PlayerState) -> List[Action]:
        """Generate all possible actions involving Joker cards."""
        joker_actions = []
        joker_cards = [card for card in player.list_card if card.rank == "JKR"]

        for joker in joker_cards:
            for suit in GameState.LIST_SUIT:
                for rank in GameState.LIST_RANK[:-1]:  # Exclude "JKR" itself
                    joker_actions.append(
                        Action(card=joker, card_swap=Card(suit=suit, rank=rank))
                    )
        return joker_actions

    def validate_marble_movement(self, start_pos: int, end_pos: int, is_safe: bool) -> bool:
        """
        Check if moving from start_pos to end_pos overtakes another marble
        or exceeds the finish bounds.

        Args:
            start_pos (int): The starting position of the marble.
            end_pos (int): The destination position of the marble.
            is_safe (bool): Whether the marble is in a safe state (e.g., moved out of the kennel).

        Returns:
            bool: True if the move is valid; False otherwise.
        """
        # Check that the move stays within the finish bounds (positions 92-95)
        if start_pos >= 92:
            if end_pos >= 96:  # Exceeding the finish area
                return False
            if start_pos <= end_pos < 96:  # Valid within finish bounds
                return True

        # Validate movement with respect to other marbles
        for player in self.state.list_player:  # Check all players
            for marble in player.list_marble:  # Check all marbles of each player
                if marble.is_save and marble.pos != -1:  # Only consider safe marbles on the board
                    # Check overtaking logic
                    if start_pos < end_pos:  # Moving forward
                        if start_pos < marble.pos <= end_pos:
                            return False  # Invalid overtaking
                    else:  # Moving forward across position 0
                        if marble.pos > start_pos or marble.pos <= end_pos:
                            return False  # Invalid overtaking across 0
        return True  # Valid move



    def finalize_turn(self):
        """Finalize the current player's turn."""
        self.state.card_active = None
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        # If the round ends, increment the round counter and deal new cards
        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.cnt_round += 1
            self.distribute_round_cards()

    def generate_player_actions(self) -> List[Action]:
        """Generate all possible actions for the active player."""
        active_player = self.state.list_player[self.state.idx_player_active]
        possible_actions = []

        # Add card exchange moves if needed
        if not self.state.bool_card_exchanged:
            return self.create_card_swap_moves(active_player)

        # Add moves for marbles in the kennel
        possible_actions.extend(self.create_moves_from_kennel(active_player))

        # Add Joker-specific actions
        possible_actions.extend(self.generate_joker_options(active_player))

        # Add normal marble movement actions
        for marble in active_player.list_marble:
            if marble.pos >= 0:  # Marble is on the board
                for card in active_player.list_card:
                    move_distances = MOVES[card.rank]
                    for move in move_distances:
                        destination = (marble.pos + move) % 96
                        if self.validate_marble_movement(marble.pos, destination, marble.is_save):
                            possible_actions.append(
                                Action(card=card, pos_from=marble.pos, pos_to=destination)
                            )
        return possible_actions

    def send_opponent_marble_home(self, position: int):
        """Send an opponent's marble back to the kennel if it occupies the target position."""
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == position:
                    kennel_position = KennelNumbers[player.colour].value[0]
                    marble.pos = kennel_position
                    marble.is_save = False

    def check_for_game_winner(self):
        """Check if the game has a winner."""
        team1 = [self.state.list_player[0], self.state.list_player[2]]
        team2 = [self.state.list_player[1], self.state.list_player[3]]

        if all(marble.pos in range(92, 96) for player in team1 for marble in player.list_marble):
            self.state.phase = GamePhase.FINISHED
            print("Team 1 wins!")
        elif all(marble.pos in range(92, 96) for player in team2 for marble in player.list_marble):
            self.state.phase = GamePhase.FINISHED
            print("Team 2 wins!")








    def valid_finish_move(self, marble: Marble, move: int) -> bool:
        """
        Check if the move keeps the marble within the finish area bounds.

        """
        if marble.pos >= 92:
            next_pos = marble.pos + move
            return 92 <= next_pos < 96  # Within finish range
        return True  # Normal moves are always valid


    def finish_overtaking(self, marble: Marble, move: int) -> bool:
        """
        Check if the move causes the marble to overtake another marble in the finish area.

        """
        if marble.pos >= 92:
            next_pos = marble.pos + move
            for m in self.state.list_player[self.state.idx_player_active].list_marble:
                if next_pos > m.pos >= 92:
                    return True
        return False

    def _generate_kennel_and_start_actions(self, player: PlayerState) -> List[Action]:
        start_pos = 16 * self.state.list_player.index(player)  # Compute player's start position
        if marble.pos == -1:
            for card in player.list_card:
                if card.rank in ["A", "K", "JKR"]:
                    actions.append(Action(card=card, pos_from=-1, pos_to=start_pos))


        # Check for marbles in the kennel
        marbles_in_kennel = [marble for marble in player.list_marble if marble.pos == -1]

        # Generate actions to move marbles out of the kennel
        for marble in marbles_in_kennel:
            for card in player.list_card:
                if card.rank in ['A', 'K', 'JKR']:  # Aces, Kings, or Jokers can move marbles out
                    actions.append(Action(card=card, pos_from=-1, pos_to=start_pos))

        return actions


    def _check_overtaking(
        self, current_pos: int, dest_pos: int, is_safe: bool, player: Optional[PlayerState] = None
    ) -> bool:
        """
        Check if a marble overtakes another marble in unsafe conditions or moves to a blocked position.

        Args:
            current_pos (int): The current position of the marble.
            dest_pos (int): The destination position of the marble.
            is_safe (bool): Whether the marble is in a safe state (e.g., moved out of the kennel).
            player (Optional[PlayerState]): The player whose marble is being moved. Defaults to the active player.

        Returns:
            bool: True if overtaking happens in unsafe conditions or moving to a blocked position; False otherwise.
        """
        # If no player is provided, use the active player
        if player is None:
            player = self.state.list_player[self.state.idx_player_active]

        for other_player in self.state.list_player:  # Check all players
            for marble in other_player.list_marble:  # Check all marbles of each player
                if marble.is_save and marble.pos != -1:  # Only consider safe marbles on the board
                    if marble.pos == dest_pos:
                        # Block movement if another marble occupies the destination and is marked as "is_save=True"
                        return True
                    if other_player == player:  # Own marble
                        # Blocking logic for own marbles
                        if current_pos < dest_pos and current_pos < marble.pos <= dest_pos:
                            return True
                        elif current_pos > dest_pos and (marble.pos > current_pos or marble.pos <= dest_pos):
                            return True
                    else:  # Opponent marble
                        # Allow overtaking in certain scenarios
                        if current_pos < dest_pos and current_pos < marble.pos <= dest_pos:
                            return False
                        elif current_pos > dest_pos and (marble.pos > current_pos or marble.pos <= dest_pos):
                            return False
        return False




    def get_list_action(self) -> List[Action]:
        """Get a list of possible actions for the active player."""
        active_player = self.state.list_player[self.state.idx_player_active]  # Active player
        actions: List[Action] = []

        # Generate card swap actions if cards have not been exchanged
        if not self.state.bool_card_exchanged:
            for card in active_player.list_card:
                actions.append(Action(card=card))  # Add card swap actions
            return actions

        for card in active_player.list_card:
            if card.rank == 'JKR':
                # Joker actions: Moving from kennel and swaps
                actions.append(Action(card=card, pos_from=64, pos_to=0))

                if self.state.cnt_round == 0:
                    # Early game: Joker can swap with A or K
                    for suit in GameState.LIST_SUIT:
                        actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='A')))
                        actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank='K')))
                else:
                    # Late game: Joker can swap with all other cards
                    for suit in GameState.LIST_SUIT:
                        for rank in GameState.LIST_RANK[:-1]:  # Exclude 'JKR'
                            actions.append(Action(card=card, pos_from=None, pos_to=None, card_swap=Card(suit=suit, rank=rank)))

            else:
                for marble in active_player.list_marble:
                    # Handle start cards (A, K) for moving out of the kennel
                    if marble.pos == -1 and card.rank in ['A', 'K']:
                        if not any(m2.pos == 0 for m2 in active_player.list_marble):  # Ensure no marble is already in start position
                            actions.append(Action(card=card, pos_from=64, pos_to=0))
                    elif marble.pos >= 0 and card.rank.isdigit():
                        # Normal move for number cards
                        new_pos = (marble.pos + int(card.rank)) % 96

                        # **Check blocking before appending**
                        if self._check_if_save_marble_between_current_and_destination(marble.pos, new_pos):
                            continue  # Skip this move if blocked

                        # Add valid action
                        actions.append(Action(card=card, pos_from=marble.pos, pos_to=new_pos))

            # Jack (J) card logic: Swapping marbles
            if card.rank == 'J':
                player_positions = [m.pos for m in active_player.list_marble if m.pos >= 0]
                opponent_positions = []

                # Collect opponent positions for swapping
                for opponent in self.state.list_player:
                    if opponent != active_player:  # Ensure it's an opponent
                        for opp_marble in opponent.list_marble:
                            if opp_marble.pos >= 0 and not opp_marble.is_save:  # Valid opponent marbles
                                opponent_positions.append((opponent, opp_marble.pos))

                # Add swaps with opponents
                for p_pos in player_positions:
                    for _, o_pos in opponent_positions:
                        actions.append(Action(card=card, pos_from=p_pos, pos_to=o_pos))  # Player to opponent
                        actions.append(Action(card=card, pos_from=o_pos, pos_to=p_pos))  # Opponent to player

                # If no opponent swaps, allow swaps among player's own marbles
                if not opponent_positions:
                    for marble_1 in active_player.list_marble:
                        if marble_1.pos >= 0:
                            for marble_2 in active_player.list_marble:
                                if marble_2.pos >= 0 and marble_1 != marble_2:
                                    actions.append(Action(card=card, pos_from=marble_1.pos, pos_to=marble_2.pos))
                                    actions.append(Action(card=card, pos_from=marble_2.pos, pos_to=marble_1.pos))

        # Ensuring unique actions
        unique_actions = list({
            (action.card, action.pos_from, action.pos_to, action.card_swap): action for action in actions
        }.values())

        return unique_actions


    

    def give_cards(self, num_cards: int) -> None:
        """
        Distribute a specific number of cards to all players.
        Replenishes the draw pile if necessary.
        """
        # Debug: Expected number of cards
        print(f"Attempting to deal {num_cards} cards to each of {self.state.cnt_player} players.")

        # Check if there are enough cards in the draw pile, replenish if needed
        total_needed_cards = num_cards * self.state.cnt_player
        if len(self.state.list_card_draw) < total_needed_cards:
            print("Not enough cards in the draw pile. Replenishing from discard pile.")
            self.state.list_card_draw.extend(self.state.list_card_discard)
            random.shuffle(self.state.list_card_draw)
            self.state.list_card_discard.clear()

        # Ensure we have enough cards after replenishment
        if len(self.state.list_card_draw) < total_needed_cards:
            raise ValueError(f"Not enough cards to deal {num_cards} to each player. Only {len(self.state.list_card_draw)} cards available.")

        # Distribute cards to each player
        for player in self.state.list_player:
            player.list_card = [self.state.list_card_draw.pop() for _ in range(num_cards)]

        # Debug: Log results
        print(f"Dealt {num_cards} cards to each player. {len(self.state.list_card_draw)} cards remain in draw pile.")




    def impossible_action(self) -> None:
        """
        Handle the case when no action is possible.
        This progresses the game state to the next active player or the next round.
        """
        # Progress to the next active player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        # Check if a new round needs to start
        if self.state.idx_player_active == self.state.idx_player_started:
            # Start a new round
            self.state.cnt_round += 1

            # Calculate the number of cards for the new round
            num_cards = self.calculate_card(self.state.cnt_round)

            # Distribute cards for the new round
            self.give_cards(num_cards)

            # Ensure the active player is not the same as the starting player
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        print(f"Round {self.state.cnt_round} completed. Next active player: Player {self.state.idx_player_active + 1}.")


    def calculate_card(self, cnt_round: int) -> int:
        """
        Calculate the number of cards to deal based on the round number.
        """
        # Assuming rounds 1-5 reduce card numbers, minimum of 2 cards per round
        return max(6 - (cnt_round - 1) % 5, 2)


    def apply_action(self, action: Optional[Action]) -> None:
        """Apply the given action to the game."""
        # Get the current player
        player = self.state.list_player[self.state.idx_player_active]

        # If no action is provided, reset the state and skip the turn
        if action is None:  # Fold cards if no action is possible
            print(f"No valid action for {player.name}. Folding cards.")
            player.list_card = []  # Clear the player's cards
            self.impossible_action()  # Progress the game state
            return

        # NEW: Handle card exchange (if it's an exchange action)
        if not self.state.bool_card_exchanged:
            self.process_card_exchange(player, action)  # Handle the card exchange
            return

        # Handle JOKER swap action
        if action.card.rank == 'JKR' and action.card_swap:
            self.state.card_active = action.card_swap
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            print(f"JOKER swapped for {action.card_swap.rank} of {action.card_swap.suit}.")

        # Handle JACK (J) swap action
        elif action.card.rank == 'J' and action.pos_from is not None and action.pos_to is not None:
            # Find the marbles at the specified positions
            marble_from = next(
                (m for m in player.list_marble if m.pos == action.pos_from), None
            )
            marble_to = next(
                (m for op in self.state.list_player for m in op.list_marble if m.pos == action.pos_to), None
            )

            # Swap positions if valid marbles are found
            if marble_from and marble_to:
                marble_from.pos, marble_to.pos = marble_to.pos, marble_from.pos
                print(f"Swapped marble at {action.pos_from} with marble at {action.pos_to}.")

            # Remove the JACK card from the player's hand
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)
            self.state.card_active = None

        # Handle normal card actions (e.g., number cards, A, K)
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
                                om.pos = 72  # Send opponent marble back to Kennel
                                om.is_save = False

            elif action.pos_from is not None and action.pos_to is not None:  # Normal move
                marble = next(m for m in player.list_marble if m.pos == action.pos_from)
                move = marble.pos = action.pos_to

                # Validate finish moves
                if not self.valid_finish_move(marble, move):
                    raise ValueError("Invalid move to or within finish area.")
                if self.finish_overtaking(marble, move):
                    raise ValueError("Overtaking in the finish area is not allowed.")

                # Proceed with movement
                marble.pos = action.pos_to

            # Track the active card and remove it from the player's hand
            self.state.card_active = action.card
            player.list_card.remove(action.card)
            self.state.list_card_discard.append(action.card)

        # NEW: Check if the game has ended
        self.check_for_game_winner()

        # Enforce the condition: Player 1 must have a marble on position 12
        if self.state.idx_player_active == 0:
            self.ensure_player1_marble_at_12()

        # NEW: Reset the turn state and move to the next player
        self.finalize_turn()




    def get_player_view(self, idx_player: int) -> GameState:
        """Get a masked view of the game state for the given player."""
        return self.state


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
        # Calculate the number of cards to deal to each player
        num_cards = max(6 - (self.state.cnt_round - 1) % 5, 2)  # Cards reduce each round but never below 2

        # Debug: Check card piles before dealing
        print(f"Before dealing: {len(self.state.list_card_draw)} cards in draw pile, {len(self.state.list_card_discard)} in discard pile.")

        # Replenish the draw pile if there aren't enough cards
        total_needed_cards = num_cards * self.state.cnt_player
        if len(self.state.list_card_draw) < total_needed_cards:
            print("Not enough cards in the draw pile. Replenishing from discard pile.")
            # Add discard pile back to the draw pile and shuffle
            self.state.list_card_draw.extend(self.state.list_card_discard)
            random.shuffle(self.state.list_card_draw)
            self.state.list_card_discard.clear()

        # If there are still not enough cards after replenishment, raise an error
        if len(self.state.list_card_draw) < total_needed_cards:
            raise ValueError("Not enough cards available in the deck to deal to all players.")

        # Deal cards to players
        for player in self.state.list_player:
            player.list_card.clear()  # Clear the player's hand
            player.list_card = self.state.list_card_draw[:num_cards]
            self.state.list_card_draw = self.state.list_card_draw[num_cards:]  # Remove dealt cards from draw pile

        # Debug: Check card piles after dealing
        print(f"After dealing: {len(self.state.list_card_draw)} cards remain in draw pile, {len(self.state.list_card_discard)} in discard pile.")

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