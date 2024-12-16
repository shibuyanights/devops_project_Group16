from __future__ import annotations  # Enables forward references for type hints
import random
from enum import Enum
from typing import List, Optional, ClassVar
from pydantic import BaseModel
from server.py.game import Game, Player
import sys
import os


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
    pos: int  # position on board (-1 for Kennel, 0 to 95 for board positions)
    is_save: bool  # true if marble was moved out of kennel and was not yet moved


class PlayerState(BaseModel):
    name: str  # name of player
    list_card: List[Card]  # list of cards
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
    SETUP = 'setup'  # before the game has started
    RUNNING = 'running'  # while the game is running
    FINISHED = 'finished'  # when the game is finished


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']  # 4 suits (colors)
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',  # 13 ranks + Joker
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
                                          # 2: Move 2 spots forward
                                          Card(suit='♠', rank='2'), Card(suit='♥', rank='2'), Card(suit='♦', rank='2'),
                                          Card(suit='♣', rank='2'),
                                          # 3: Move 3 spots forward
                                          Card(suit='♠', rank='3'), Card(suit='♥', rank='3'), Card(suit='♦', rank='3'),
                                          Card(suit='♣', rank='3'),
                                          # 4: Move 4 spots forward or back
                                          Card(suit='♠', rank='4'), Card(suit='♥', rank='4'), Card(suit='♦', rank='4'),
                                          Card(suit='♣', rank='4'),
                                          # 5: Move 5 spots forward
                                          Card(suit='♠', rank='5'), Card(suit='♥', rank='5'), Card(suit='♦', rank='5'),
                                          Card(suit='♣', rank='5'),
                                          # 6: Move 6 spots forward
                                          Card(suit='♠', rank='6'), Card(suit='♥', rank='6'), Card(suit='♦', rank='6'),
                                          Card(suit='♣', rank='6'),
                                          # 7: Move 7 single steps forward
                                          Card(suit='♠', rank='7'), Card(suit='♥', rank='7'), Card(suit='♦', rank='7'),
                                          Card(suit='♣', rank='7'),
                                          # 8: Move 8 spots forward
                                          Card(suit='♠', rank='8'), Card(suit='♥', rank='8'), Card(suit='♦', rank='8'),
                                          Card(suit='♣', rank='8'),
                                          # 9: Move 9 spots forward
                                          Card(suit='♠', rank='9'), Card(suit='♥', rank='9'), Card(suit='♦', rank='9'),
                                          Card(suit='♣', rank='9'),
                                          # 10: Move 10 spots forward
                                          Card(suit='♠', rank='10'), Card(suit='♥', rank='10'),
                                          Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
                                          # Jake: A marble must be exchanged
                                          Card(suit='♠', rank='J'), Card(suit='♥', rank='J'), Card(suit='♦', rank='J'),
                                          Card(suit='♣', rank='J'),
                                          # Queen: Move 12 spots forward
                                          Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'), Card(suit='♦', rank='Q'),
                                          Card(suit='♣', rank='Q'),
                                          # King: Start or move 13 spots forward
                                          Card(suit='♠', rank='K'), Card(suit='♥', rank='K'), Card(suit='♦', rank='K'),
                                          Card(suit='♣', rank='K'),
                                          # Ass: Start or move 1 or 11 spots forward
                                          Card(suit='♠', rank='A'), Card(suit='♥', rank='A'), Card(suit='♦', rank='A'),
                                          Card(suit='♣', rank='A'),
                                          # Joker: Use as any other card you want
                                          Card(suit='', rank='JKR'), Card(suit='', rank='JKR'),
                                          Card(suit='', rank='JKR')
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


# Main Dog class
class Dog(Game):

    def __init__(self) -> None:
        self.steps_remaining = None
        self.seven_card_backup = None  # Backup for SEVEN card scenario
        self.reset()

    def reset(self) -> None:
        draw_pile = list(GameState.LIST_CARD)
        random.shuffle(draw_pile)

        players = []
        for i in range(4):
            # Slightly change how marbles are initialized
            marbles = [
                Marble(pos=(64 + i * 8 + j), is_save=(j == 0))  # Set the first marble as "is_save=True"
                for j in range(4)
            ]

            # Assign cards to the player
            player_cards = draw_pile[:6]
            draw_pile = draw_pile[6:]

            players.append(PlayerState(
                name=f"Player {i + 1}",
                list_card=player_cards,
                list_marble=marbles
            ))

        self.state = GameState(
            cnt_player=4,
            phase=GamePhase.RUNNING,
            cnt_round=1,
            bool_card_exchanged=False,
            idx_player_started=0,
            idx_player_active=0,
            list_player=players,
            list_card_draw=draw_pile,
            list_card_discard=[],
            card_active=None
        )

    def set_state(self, state: GameState) -> None:
        self.state = state

    def get_state(self) -> GameState:
        return self.state

    def print_state(self) -> None:
        pass

    def is_path_blocked(self, start: int, end: int) -> bool:
        """Helper function to check blocking marbles on path"""
        # Assuming forward moves on the main loop. Check intermediate positions for blocking marbles.
        step = 1 if end > start else -1
        for pos in range(start + step, end + step, step):
            for player in self.state.list_player:
                for m in player.list_marble:
                    # If a marble is on this position and is_save is True, it blocks movement.
                    if m.pos == pos and m.is_save:
                        return True
        return False

    def generate_joker_actions(game, active_player, card):
        actions = []
        for marble in active_player.list_marble:
            if marble.pos == 64:  # Kennel position
                actions.append(Action(card=card, pos_from=64, pos_to=0))
        return actions

    def generate_start_card_actions(game, active_player, card):
        actions = []
        for marble in active_player.list_marble:
            if marble.pos == 64:  # Kennel position
                actions.append(Action(card=card, pos_from=64, pos_to=0))
        return actions

    def generate_jack_actions(game, active_player, card):
        actions = []
        for marble in active_player.list_marble:
            if marble.pos < 64:
                for opponent in game.state.list_player:
                    if opponent != active_player:
                        for opp_marble in opponent.list_marble:
                            if not opp_marble.is_save and opp_marble.pos < 64:
                                actions.append(Action(card=card, pos_from=marble.pos, pos_to=opp_marble.pos))
                                actions.append(Action(card=card, pos_from=opp_marble.pos, pos_to=marble.pos))
        return actions

    def generate_numbered_card_actions(game, active_player, card, steps):
        actions = []
        for marble in active_player.list_marble:
            if 0 <= marble.pos < 64:
                target_pos = marble.pos + steps
                if target_pos <= 63 and not game.is_path_blocked(marble.pos, target_pos):
                    actions.append(Action(card=card, pos_from=marble.pos, pos_to=target_pos))
        return actions


    def fold_cards(self, player: PlayerState) -> None:
        """Discard all cards in hand when no valid action is possible."""
        self.state.list_card_discard.extend(player.list_card)
        player.list_card.clear()
        print(f"{player.name} folded their cards.")
        self._finalize_turn()

    def get_list_action(self) -> List[Action]:
        actions = []
        active_player = self.state.list_player[self.state.idx_player_active]

        cards = active_player.list_card if not self.state.card_active else [self.state.card_active]

        # Check if it's the beginning of the game (all marbles in kennel)
        is_beginning_phase = all(marble.pos >= 64 for marble in active_player.list_marble)

        for card in cards:
            if card.rank == 'JKR':
                actions.extend(self._generate_joker_actions(active_player, card, is_beginning_phase))
            elif card.rank in ['A', 'K']:
                actions.extend(self._generate_start_card_actions(active_player, card))
            elif card.rank == 'J':
                actions.extend(self._generate_jack_card_actions(active_player, card))
            elif card.rank in {'2', '3', '5', '6', '8', '9', '10'}:
                actions.extend(self._generate_forward_move_actions(active_player, card))

        return actions

    def _generate_joker_actions(self, active_player: PlayerState, card: Card, is_beginning_phase: bool) -> List[Action]:
        """Generate actions for Joker cards."""
        actions = []

        # Move from kennel to start
        for marble in active_player.list_marble:
            if marble.pos == 64:  # Marble in kennel
                actions.append(Action(
                    card=card,
                    pos_from=64,
                    pos_to=0,
                    card_swap=None
                ))

        # Swap actions
        if is_beginning_phase:
            # Limited swap actions at the beginning
            for suit in GameState.LIST_SUIT:
                for rank in ['A', 'K']:
                    actions.append(Action(
                        card=card,
                        pos_from=None,
                        pos_to=None,
                        card_swap=Card(suit=suit, rank=rank)
                    ))
        else:
            # All valid swap actions later
            for suit in GameState.LIST_SUIT:
                for rank in GameState.LIST_RANK:
                    if rank != 'JKR':  # Cannot swap with another Joker
                        actions.append(Action(
                            card=card,
                            pos_from=None,
                            pos_to=None,
                            card_swap=Card(suit=suit, rank=rank)
                        ))

        return actions

    def _generate_start_card_actions(self, active_player: PlayerState, card: Card) -> List[Action]:
        """Generate actions for start cards (A and K)."""
        actions = []

        for marble in active_player.list_marble:
            if marble.pos == 64:  # Marble in kennel
                actions.append(Action(
                    card=card,
                    pos_from=64,
                    pos_to=0,
                    card_swap=None
                ))

        return actions

    def _generate_jack_card_actions(self, active_player: PlayerState, card: Card) -> List[Action]:
        """Generate actions for Jack (J) cards."""
        actions = []
        found_valid_target = False

        # Swap with opponent marbles
        for marble in active_player.list_marble:
            if marble.pos < 64:  # Marble on board
                for opponent in self.state.list_player:
                    if opponent != active_player:
                        for opp_marble in opponent.list_marble:
                            if not opp_marble.is_save and opp_marble.pos < 64:
                                found_valid_target = True
                                # Forward swap
                                actions.append(Action(
                                    card=card,
                                    pos_from=marble.pos,
                                    pos_to=opp_marble.pos,
                                    card_swap=None
                                ))
                                # Reverse swap
                                actions.append(Action(
                                    card=card,
                                    pos_from=opp_marble.pos,
                                    pos_to=marble.pos,
                                    card_swap=None
                                ))

        # If no valid opponents, generate self-swapping actions
        if not found_valid_target:
            marbles_on_board = [
                marble for marble in active_player.list_marble if marble.pos < 64
            ]
            for i in range(len(marbles_on_board)):
                for j in range(i + 1, len(marbles_on_board)):
                    actions.append(Action(
                        card=card,
                        pos_from=marbles_on_board[i].pos,
                        pos_to=marbles_on_board[j].pos,
                        card_swap=None
                    ))
                    actions.append(Action(
                        card=card,
                        pos_from=marbles_on_board[j].pos,
                        pos_to=marbles_on_board[i].pos,
                        card_swap=None
                    ))

        return actions

    def _generate_forward_move_actions(self, active_player: PlayerState, card: Card) -> List[Action]:
        """Generate forward move actions for numbered cards."""
        actions = []
        forward_move_cards = {
            '2': 2, '3': 3, '5': 5, '6': 6, '8': 8, '9': 9, '10': 10
        }
        steps = forward_move_cards[card.rank]

        for marble in active_player.list_marble:
            if 0 <= marble.pos < 64:
                target_pos = marble.pos + steps
                if target_pos <= 63:  # On the main board
                    # Check path for blocking
                    if not self.is_path_blocked(marble.pos, target_pos):
                        actions.append(Action(
                            card=card,
                            pos_from=marble.pos,
                            pos_to=target_pos
                        ))

        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        # Reshuffle cards if the draw pile is empty
        if not self.state.list_card_draw:
            self.reshuffle_cards()

        active_player = self.state.list_player[self.state.idx_player_active]

        # Handle when no action is provided
        if action is None:
            self._handle_no_action(active_player)
            return

        # Handle specific card actions
        if action.card.rank == '7':
            self._handle_seven_card(action, active_player)
        elif action.card.rank == 'JKR':
            # Handle JOKER card
            if action.card_swap:
                # Remove the JOKER card from the player's hand
                active_player.list_card.remove(action.card)

                # Set the swapped card as the active card
                self.state.card_active = action.card_swap
                print(f"JOKER played: Active card is now {self.state.card_active}.")
                return
        elif action.card.rank == 'J':
            self._handle_jack_card(action, active_player)
        else:
            self._handle_normal_card(action, active_player)

        # Finalize turn if no steps are remaining
        if self.steps_remaining is None:
            self._finalize_turn()

        # Check for victory after the action
        winner = self.check_victory()
        if winner:
            print(f"Player {winner} has won the game!")

    def reshuffle_cards(self) -> None:
        """Reshuffle the discard pile into the draw pile if there are no cards left."""
        if not self.state.list_card_draw and self.state.list_card_discard:
            # Move all discard pile cards into the draw pile
            self.state.list_card_draw.extend(self.state.list_card_discard)
            self.state.list_card_discard.clear()
            random.shuffle(self.state.list_card_draw)
            print("Reshuffled the discard pile into the draw pile.")

        self._validate_card_count()


    def _validate_card_count(self) -> None:
        """Validate that the total number of cards in the game is consistent."""
        total_cards = len(self.state.list_card_draw) + len(self.state.list_card_discard)
        for player in self.state.list_player:
            total_cards += len(player.list_card)

        # Debugging: Print the breakdown of card counts
        print(f"Draw pile: {len(self.state.list_card_draw)}, Discard pile: {len(self.state.list_card_discard)}")
        for idx, player in enumerate(self.state.list_player):
            print(f"Player {idx + 1} cards: {len(player.list_card)}")

        if total_cards != 110:
            raise ValueError(f"Error: Total number of cards is {total_cards}, but it must be 110.")

    def _handle_no_action(self, active_player: PlayerState) -> None:
        """Handle cases where no action is provided."""
        print("No action provided; skipping turn or reshuffling cards.")
        # If we are in the middle of a SEVEN card action and cannot complete all steps
        if self.state.card_active and self.state.card_active.rank == '7' and self.steps_remaining is not None:
            # Revert to the backup state
            self._restore_seven_card_backup()
            # After restoring, do not finalize turn or fold here, just return
            return
        else:
            if self.state.card_active and self.state.card_active.rank == '7':
                self._finalize_turn()
            else:
                self.fold_cards(active_player)

    def _handle_seven_card(self, action: Action, active_player: PlayerState) -> None:
        """Handle SEVEN card actions with split movements."""
        if self.steps_remaining is None:
            self.steps_remaining = 7
            self.state.card_active = action.card
            # Backup the state before any moves for SEVEN card
            self.seven_card_backup = self._create_seven_card_backup()

        steps_used = self._calculate_steps_used(action)

        if steps_used > self.steps_remaining:
            raise ValueError("Exceeded remaining steps for SEVEN.")

        moving_marble = self._get_marble_at_position(active_player, action.pos_from)
        if moving_marble:
            self._handle_intermediate_positions(action, moving_marble, active_player)
            moving_marble.pos = action.pos_to
            self.steps_remaining -= steps_used

            if self.steps_remaining == 0:
                self.steps_remaining = None
                self.state.card_active = None
                active_player.list_card.remove(action.card)
                self.seven_card_backup = None  # Clear backup after successful completion

    def _handle_joker_card(self, action: Action, active_player: PlayerState) -> None:
        """Handle JOKER card swap logic."""
        if action.card_swap:
            self.state.card_active = action.card_swap
            active_player.list_card.remove(action.card)

    def _handle_jack_card(self, action: Action, active_player: PlayerState) -> None:
        """Handle JACK card swapping of marbles."""
        moving_marble = self._get_marble_at_position(active_player, action.pos_from)
        opponent_marble = self._get_marble_at_position_of_opponent(action.pos_to)

        if moving_marble and opponent_marble:
            moving_marble.pos, opponent_marble.pos = opponent_marble.pos, moving_marble.pos

    def _handle_normal_card(self, action: Action, active_player: PlayerState) -> None:
        """Handle normal card actions."""
        moving_marble = self._get_marble_at_position(active_player, action.pos_from)
        if moving_marble:
            opponent_marble = self._get_marble_at_position_of_opponent(action.pos_to)
            if opponent_marble:
                opponent_marble.pos = 72  # Send opponent's marble to kennel
                opponent_marble.is_save = False
            moving_marble.pos = action.pos_to
            moving_marble.is_save = True

    def _finalize_turn(self) -> None:
        """Move to the next player's turn or finish the round."""
        # Clear the active card
        self.state.card_active = None

        # Move to the next player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        # Check if the round is complete
        if self.state.idx_player_active == self.state.idx_player_started:
            self._handle_round_completion()


    def _calculate_steps_used(self, action: Action) -> int:
        """Calculate the number of steps used for the SEVEN card."""
        if action.pos_to >= 76:  # Moving to finish
            if action.pos_from == 13:  # First move into finish area
                return 5
            return 2
        return abs(action.pos_to - action.pos_from)

    def _handle_intermediate_positions(self, action: Action, moving_marble: Marble, active_player: PlayerState) -> None:
        """Handle intermediate positions for SEVEN card."""
        for pos in range(action.pos_from + 1, action.pos_to + 1):
            opponent_marble = self._get_marble_at_position_of_opponent(pos)
            if opponent_marble:
                opponent_marble.pos = 72  # Send to kennel
                opponent_marble.is_save = False
                break
            own_marble = self._get_marble_at_position(active_player, pos)
            if own_marble and own_marble != moving_marble:
                own_marble.pos = 72  # Send to kennel
                own_marble.is_save = False
                break

    def _get_marble_at_position(self, player: PlayerState, position: int) -> Optional[Marble]:
        """Get a marble at a specific position for a player."""
        return next((m for m in player.list_marble if m.pos == position), None)

    def _get_marble_at_position_of_opponent(self, position: int) -> Optional[Marble]:
        """Get a marble at a specific position for any opponent."""
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == position:
                    return marble
        return None

    def _handle_round_completion(self) -> None:
        """Handle the completion of a round."""
        self.state.cnt_round += 1
        self.state.bool_card_exchanged = False
        self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player

        cards_per_player = self._calculate_cards_per_round()
        self._reshuffle_if_needed(cards_per_player)
        self._deal_cards(cards_per_player)

    def _calculate_cards_per_round(self) -> int:
        """Calculate the number of cards to deal in the current round."""
        if 1 <= self.state.cnt_round <= 5:
            return 7 - self.state.cnt_round
        if self.state.cnt_round == 6:
            return 6
        return max(7 - ((self.state.cnt_round - 1) % 5 + 1), 2)

    def _reshuffle_if_needed(self, cards_per_player: int) -> None:
        """Reshuffle the deck if there are not enough cards to deal."""
        total_cards_needed = cards_per_player * self.state.cnt_player
        if len(self.state.list_card_draw) < total_cards_needed:
            self.state.list_card_draw = list(GameState.LIST_CARD)
            random.shuffle(self.state.list_card_draw)
            self.state.list_card_discard = []

    def _deal_cards(self, cards_per_player: int) -> None:
        """Deal cards to players for the next round. Reshuffle if needed."""
        self.reshuffle_cards()  # Ensure there are enough cards in the draw pile

        draw_pile = self.state.list_card_draw
        for player in self.state.list_player:
            player.list_card = draw_pile[:cards_per_player]
            draw_pile = draw_pile[cards_per_player:]

        # Update the draw pile
        self.state.list_card_draw = draw_pile

    def check_victory(self) -> Optional[str]:
        """Check if any player has won the game."""
        if self.state.phase == GamePhase.FINISHED:
            return None  # Avoid re-checking if the game is already finished

        for player in self.state.list_player:
            if all(76 <= marble.pos <= 95 for marble in player.list_marble):  # All marbles in the finish zone
                if self.state.phase != GamePhase.FINISHED:  # Ensure winner is announced only once
                    print(f"Player {player.name} has won the game!")
                    self.state.phase = GamePhase.FINISHED
                return player.name
        return None

    def get_player_view(self, idx_player: int) -> GameState:
        """
        Return a masked view of the game state for the given player.
        Players cannot see other players' cards.
        """
        masked_players = []
        for idx, player in enumerate(self.state.list_player):
            if idx == idx_player:
                # Full visibility for the current player
                masked_players.append(player)
            else:
                # Mask other players' cards but show marble positions
                masked_players.append(
                    PlayerState(
                        name=player.name,
                        list_card=[],  # Hide cards
                        list_marble=player.list_marble,  # Show marbles
                    )
                )

        return GameState(
            cnt_player=self.state.cnt_player,
            phase=self.state.phase,
            cnt_round=self.state.cnt_round,
            bool_card_exchanged=self.state.bool_card_exchanged,
            idx_player_started=self.state.idx_player_started,
            idx_player_active=self.state.idx_player_active,
            list_player=masked_players,
            list_card_draw=[],  # Hide the draw pile
            list_card_discard=[],  # Hide the discard pile
            card_active=self.state.card_active,
        )

    def _create_seven_card_backup(self):
        """Create a backup of the current state before starting SEVEN card moves."""
        return {
            'marbles': [
                (player_idx, marble_idx, marble.pos, marble.is_save)
                for player_idx, p in enumerate(self.state.list_player)
                for marble_idx, marble in enumerate(p.list_marble)
            ],
            'card_hands': [
                (player_idx, list(p.list_card))
                for player_idx, p in enumerate(self.state.list_player)
            ],
            'card_active': self.state.card_active,
            'steps_remaining': self.steps_remaining,
            'idx_player_active': self.state.idx_player_active,
        }

    def _restore_seven_card_backup(self):
        """Restore the game state from the backup if the SEVEN action was not completed."""
        if not self.seven_card_backup:
            return

        # Restore marbles
        for player_idx, marble_idx, pos, is_save in self.seven_card_backup['marbles']:
            self.state.list_player[player_idx].list_marble[marble_idx].pos = pos
            self.state.list_player[player_idx].list_marble[marble_idx].is_save = is_save

        # Restore cards
        for player_idx, card_list in self.seven_card_backup['card_hands']:
            self.state.list_player[player_idx].list_card = card_list

        # Restore active card and steps
        self.state.card_active = None
        self.steps_remaining = None
        self.seven_card_backup = None

class RandomPlayer(Player):

    def select_action(self, state: GameState, actions: List[Action]) -> Optional[Action]:
        if len(actions) > 0:
            return random.choice(actions)
        return None

if __name__ == '__main__':
    game = Dog()
    game.start_new_round()  # Start a new round for testing
    game.print_state()