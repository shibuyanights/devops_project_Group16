from __future__ import annotations  # Enables forward references for type hints
from collections import Counter
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
        self.card_exchange_buffer = [None, None, None, None]
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
        step = 1 if end > start else -1
        for pos in range(start + step, end + step, step):
            for player in self.state.list_player:
                for m in player.list_marble:
                    if m.pos == pos and m.is_save:
                        return True
        return False

    def fold_cards(self, player: PlayerState) -> None:
        """Discard all cards in hand when no valid action is possible."""
        self.state.list_card_discard.extend(player.list_card)
        player.list_card.clear()
        print(f"{player.name} folded their cards.")
        self._finalize_turn()

    def _send_marble_home(self, marble: Marble) -> None:
        """Send a marble back to its owner's kennel."""
        owner_idx = self._get_marble_owner(marble)
        # Owner kennel starts at 64 + owner_idx*8
        kennel_start = 64 + owner_idx * 8
        marble.pos = kennel_start
        marble.is_save = False

    def _get_marble_owner(self, marble: Marble) -> int:
        for i, player in enumerate(self.state.list_player):
            if marble in player.list_marble:
                return i
        return -1
    
    def is_player_finished(self, player_idx: int) -> bool:
        """Check if a player has all marbles in the finish area."""
        player = self.state.list_player[player_idx]
        start_finish = 68 + 8 * player_idx
        return all(start_finish <= m.pos <= start_finish + 3 for m in player.list_marble)
    
    def get_partner_index(self, player_idx: int) -> int:
        """Return the partner's index for the given player (0 & 2 are partners, 1 & 3 are partners)."""
        return (player_idx + 2) % self.state.cnt_player


    def get_active_and_partner_marbles(self) -> List[Marble]:
        """Get marbles that the active player can move, including partner’s if finished."""
        active_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_idx]
        marbles = list(active_player.list_marble)
        if self.is_player_finished(active_idx):
            partner_idx = self.get_partner_index(active_idx)
            partner = self.state.list_player[partner_idx]
            marbles.extend(partner.list_marble)
        return marbles
    
    def get_active_and_partner_playerstates(self) -> List[PlayerState]:
        """Get player states (active and partner) if active is finished, else just active player."""
        active_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_idx]
        if self.is_player_finished(active_idx):
            partner_idx = self.get_partner_index(active_idx)
            partner = self.state.list_player[partner_idx]
            return [active_player, partner]
        return [active_player]
    

    def _find_marble_by_pos(self, marbles: List[Marble], pos: int) -> Optional[Marble]:
        """Find a marble by position in a given list of marbles."""
        return next((m for m in marbles if m.pos == pos), None)
    
    def get_list_action(self) -> List[Action]:
        actions = set()
        active_player = self.state.list_player[self.state.idx_player_active]

        # Card exchange phase at start of round 0 (similar logic as before)
        if not self.state.bool_card_exchanged and self.state.cnt_round == 0:
            for c in active_player.list_card:
                actions.add(Action(card=c, pos_from=None, pos_to=None, card_swap=None))
            return list(actions)

        # MODIFIED: If active player finished, consider both active and partner marbles
        marbles_to_consider = self.get_active_and_partner_marbles()

        cards = active_player.list_card if not self.state.card_active else [self.state.card_active]

        is_beginning_phase = all(marble.pos >= 64 for marble in active_player.list_marble)

        for card in cards:
            if card.rank == 'JKR':
                actions.update(self._generate_joker_actions(active_player, card, is_beginning_phase, marbles_to_consider))  # MODIFIED
            elif card.rank in ['A', 'K']:
                actions.update(self._generate_start_card_actions(active_player, card, marbles_to_consider))  # MODIFIED
            elif card.rank == 'J':
                actions.update(self._generate_jack_card_actions(active_player, card, marbles_to_consider))  # MODIFIED
            elif card.rank in {'2', '3', '5', '6', '8', '9', '10'}:
                actions.update(self._generate_forward_move_actions(active_player, card, marbles_to_consider))  # MODIFIED

        return list(actions)

    def _find_duplicate_actions(self, actions: List[Action]) -> None:
        """Detect and print duplicate actions for debugging."""
        action_counter = Counter(actions)
        duplicates = [action for action, count in action_counter.items() if count > 1]

        if duplicates:
            print("Duplicate actions found:")
            for action in duplicates:
                print(action)
            raise ValueError("Duplicate actions detected in get_list_action.")
        else:
            print("No duplicate actions found.")

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
        actions = []

        for marble in active_player.list_marble:
            if marble.pos == 64:  # Marble in kennel
                actions.append(Action(
                    card=card,
                    pos_from=64,
                    pos_to=0,  # Move to starting position
                    card_swap=None
                ))

            # Check for other valid moves forward
            if 0 <= marble.pos < 64:
                target_pos = marble.pos + 1  # A moves 1 or 11 steps (this is simplified)
                if target_pos <= 63:
                    actions.append(Action(
                        card=card,
                        pos_from=marble.pos,
                        pos_to=target_pos
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
        # Check if draw pile is empty and reshuffle if needed
        if not self.state.list_card_draw:
            self.reshuffle_cards()

        if not self.state.bool_card_exchanged and self.state.cnt_round == 0:
            active_player = self.state.list_player[self.state.idx_player_active]
            if action is None or action.card not in active_player.list_card:
                print("Invalid action: Card exchange requires choosing one of your cards.")
                return
            chosen_card = action.card
            active_player.list_card.remove(chosen_card)
            self.card_exchange_buffer[self.state.idx_player_active] = chosen_card
            self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

            if all(c is not None for c in self.card_exchange_buffer):
                for i in range(self.state.cnt_player):
                    partner_idx = (i + 2) % self.state.cnt_player
                    self.state.list_player[i].list_card.append(self.card_exchange_buffer[partner_idx])
                self.card_exchange_buffer = [None, None, None, None]
                self.state.bool_card_exchanged = True
                self.state.idx_player_active = self.state.idx_player_started
            return

        if not self.state.list_card_draw:
            self.reshuffle_cards()

        active_player_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_player_idx]

        # ADDED: If player finished, consider marbles of partner too
        marbles_to_consider = self.get_active_and_partner_marbles()

        if action is None:
            self._handle_no_action(active_player)
            return

        # Instead of just active_player marbles, use marbles_to_consider
        if action.card.rank == '7':
            self._handle_seven_card(action, active_player)
        elif action.card.rank == 'JKR':
            if action.card_swap:
                active_player.list_card.remove(action.card)
                self.state.card_active = action.card_swap
                print(f"JOKER played: Active card is now {self.state.card_active}.")
                return
        elif action.card.rank == 'J':
            self._handle_jack_card_in_apply(action, active_player, marbles_to_consider)  # ADDED helper call
        else:
            self._handle_normal_card_in_apply(action, active_player, marbles_to_consider)  # ADDED helper call

        if self.steps_remaining is None:
            self._finalize_turn()

        winner = self.check_victory()
        if winner:
            pass

    def reshuffle_cards(self, cards_per_player: Optional[int] = None) -> None:
        # Calculate how many cards are needed
        total_cards_needed = (cards_per_player * self.state.cnt_player) if cards_per_player else 0

        # If we specifically need a certain number of cards and we don't have enough,
        # or if draw pile is empty, try to refill.
        while (cards_per_player and len(self.state.list_card_draw) < total_cards_needed) or (not self.state.list_card_draw):
            if self.state.list_card_discard:
                # If we have discarded cards, move them to the draw pile and shuffle
                self.state.list_card_draw.extend(self.state.list_card_discard)
                self.state.list_card_discard.clear()
                random.shuffle(self.state.list_card_draw)
            else:
                # No discard pile available, restore the original deck
                self.state.list_card_draw = list(GameState.LIST_CARD)
                random.shuffle(self.state.list_card_draw)
                self.state.list_card_discard.clear()

        self._validate_card_count()

    def _exchange_cards(self, player: PlayerState, action: Optional[Action]) -> None:
        # Check if action is valid
        if action is None or action.card is None or action.card_swap is None:
            print("Invalid action: Card exchange requires both a card and a card to swap.")
            return

        # Identify the partner player
        idx_partner = (self.state.idx_player_active + 2) % self.state.cnt_player
        partner = self.state.list_player[idx_partner]

        # Exchange the cards
        player.list_card.remove(action.card)
        partner.list_card.append(action.card)

        partner.list_card.remove(action.card_swap)
        player.list_card.append(action.card_swap)

        # Move to the next player
        self.state.idx_player_active = (self.state.idx_player_active + 1) % self.state.cnt_player

        # Mark exchange as complete if we've cycled through all players
        if self.state.idx_player_active == self.state.idx_player_started:
            self.state.bool_card_exchanged = True

    def _validate_card_count(self) -> None:
        """Validate that the total number of cards in the game is consistent."""
        total_cards = len(self.state.list_card_draw) + len(self.state.list_card_discard)
        for player in self.state.list_player:
            total_cards += len(player.list_card)

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
                # Send opponent marble home properly
                self._send_marble_home(opponent_marble)
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

    def start_new_round(self) -> None:
        """Start a new round: reshuffle cards and deal to players."""
        self._handle_round_completion()
        print(f"Round {self.state.cnt_round} started.")

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
                self._send_marble_home(opponent_marble)
                break
            own_marble = self._get_marble_at_position(active_player, pos)
            if own_marble and own_marble != moving_marble:
                self._send_marble_home(own_marble)
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
        """Handle the completion of a round and prepare for the next round."""
        self.state.cnt_round += 1  # Increment the round counter
        self.state.bool_card_exchanged = False
        self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player
        
        # Calculate the correct number of cards for the next round
        cards_per_player = self._calculate_cards_per_round()

        # Reshuffle cards and deal to players
        self.reshuffle_cards(cards_per_player)
        self._deal_cards(cards_per_player)
        print(f"Round {self.state.cnt_round} started with {cards_per_player} cards per player.")

    def _calculate_cards_per_round(self) -> int:
        """Calculate the number of cards to deal in the current round."""
        if 1 <= self.state.cnt_round <= 5:
            return 7 - self.state.cnt_round
        return 7 - ((self.state.cnt_round - 1) % 5 + 1)

    def _deal_cards(self, cards_per_player: int) -> None:
        """Deal a specific number of cards to each player."""
        self.reshuffle_cards()  # Ensure enough cards are available
        draw_pile = self.state.list_card_draw

        for player in self.state.list_player:
            player.list_card = draw_pile[:cards_per_player]
            draw_pile = draw_pile[cards_per_player:]

        self.state.list_card_draw = draw_pile  # Update remaining draw pile

    def check_victory(self) -> Optional[str]:
        """Check if any player has won the game."""
        if self.state.phase == GamePhase.FINISHED:
            return None  # Avoid re-checking if the game is already finished

        for player in self.state.list_player:
            if all(76 <= marble.pos <= 95 for marble in player.list_marble):  # All marbles in finish zone
                if self.state.phase != GamePhase.FINISHED:  # Ensure winner is announced only once
                    self.state.phase = GamePhase.FINISHED  # Stop game phase
                    print(f"Player {player.name} has won the game!")
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