from __future__ import annotations  # Enables forward references for type hints

import random
from collections import Counter
from enum import Enum
from typing import (
    Any, ClassVar, Dict, List, Optional, Set, cast
)

from pydantic import BaseModel

from server.py.game import Game, Player



class Card(BaseModel):
    suit: str
    rank: str

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return str(self) < str(other)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self.suit == other.suit and self.rank == other.rank

    def __str__(self) -> str:
        return f"{self.suit}{self.rank}"

    def __hash__(self) -> int:
        return hash((self.suit, self.rank))


class Marble(BaseModel):
    pos: int
    is_save: bool


class PlayerState(BaseModel):
    name: str
    list_card: List[Card]
    list_marble: List[Marble]


class Action(BaseModel):
    card: Card
    pos_from: Optional[int] = None
    pos_to: Optional[int] = None
    card_swap: Optional[Card] = None

    def __hash__(self) -> int:
        return hash((self.card, self.pos_from, self.pos_to, self.card_swap))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Action):
            return False
        return (
            self.card == other.card
            and self.pos_from == other.pos_from
            and self.pos_to == other.pos_to
            and self.card_swap == other.card_swap
        )


class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class GameState(BaseModel):
    LIST_SUIT: ClassVar[List[str]] = ['♠', '♥', '♦', '♣']
    LIST_RANK: ClassVar[List[str]] = [
        '2', '3', '4', '5', '6', '7', '8', '9', '10',
        'J', 'Q', 'K', 'A', 'JKR'
    ]
    LIST_CARD: ClassVar[List[Card]] = [
        Card(suit='♠', rank='2'), Card(suit='♥', rank='2'),
        Card(suit='♦', rank='2'), Card(suit='♣', rank='2'),
        Card(suit='♠', rank='3'), Card(suit='♥', rank='3'),
        Card(suit='♦', rank='3'), Card(suit='♣', rank='3'),
        Card(suit='♠', rank='4'), Card(suit='♥', rank='4'),
        Card(suit='♦', rank='4'), Card(suit='♣', rank='4'),
        Card(suit='♠', rank='5'), Card(suit='♥', rank='5'),
        Card(suit='♦', rank='5'), Card(suit='♣', rank='5'),
        Card(suit='♠', rank='6'), Card(suit='♥', rank='6'),
        Card(suit='♦', rank='6'), Card(suit='♣', rank='6'),
        Card(suit='♠', rank='7'), Card(suit='♥', rank='7'),
        Card(suit='♦', rank='7'), Card(suit='♣', rank='7'),
        Card(suit='♠', rank='8'), Card(suit='♥', rank='8'),
        Card(suit='♦', rank='8'), Card(suit='♣', rank='8'),
        Card(suit='♠', rank='9'), Card(suit='♥', rank='9'),
        Card(suit='♦', rank='9'), Card(suit='♣', rank='9'),
        Card(suit='♠', rank='10'), Card(suit='♥', rank='10'),
        Card(suit='♦', rank='10'), Card(suit='♣', rank='10'),
        Card(suit='♠', rank='J'), Card(suit='♥', rank='J'),
        Card(suit='♦', rank='J'), Card(suit='♣', rank='J'),
        Card(suit='♠', rank='Q'), Card(suit='♥', rank='Q'),
        Card(suit='♦', rank='Q'), Card(suit='♣', rank='Q'),
        Card(suit='♠', rank='K'), Card(suit='♥', rank='K'),
        Card(suit='♦', rank='K'), Card(suit='♣', rank='K'),
        Card(suit='♠', rank='A'), Card(suit='♥', rank='A'),
        Card(suit='♦', rank='A'), Card(suit='♣', rank='A'),
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


class Dog(Game):
    state: GameState

    def __init__(self) -> None:
        self.steps_remaining: Optional[int] = None
        self.seven_card_backup: Optional[Dict[str, Any]] = None
        self.card_exchange_buffer: List[Optional[Card]] = [
            None, None, None, None
        ]

        self.reset()

    def reset(self) -> None:
        draw_pile: List[Card] = list(GameState.LIST_CARD)
        random.shuffle(draw_pile)

        players: List[PlayerState] = []
        for i in range(4):
            marbles: List[Marble] = [
                Marble(pos=(64 + i * 8 + j), is_save=j == 0)
                for j in range(4)
            ]
            player_cards: List[Card] = draw_pile[:6]
            draw_pile = draw_pile[6:]
            players.append(
                PlayerState(
                    name=f"Player {i + 1}",
                    list_card=player_cards,
                    list_marble=marbles
                )
            )

        self.state: GameState = GameState(
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
        step = 1 if end > start else -1
        for pos in range(start + step, end + step, step):
            for player in self.state.list_player:
                for m in player.list_marble:
                    if m.pos == pos and m.is_save:
                        return True
        return False

    def fold_cards(self, player: PlayerState) -> None:
        self.state.list_card_discard.extend(player.list_card)
        player.list_card.clear()
        print(f"{player.name} folded their cards.")
        self._finalize_turn()

    def _send_marble_home(self, marble: Marble) -> None:
        owner_idx = self._get_marble_owner(marble)
        kennel_start = 64 + owner_idx * 8
        marble.pos = kennel_start
        marble.is_save = False

    def _get_marble_owner(self, marble: Marble) -> int:
        for i, player in enumerate(self.state.list_player):
            if marble in player.list_marble:
                return i
        return -1

    def is_player_finished(self, player_idx: int) -> bool:
        player = self.state.list_player[player_idx]
        start_finish = 68 + 8 * player_idx
        return all(
            start_finish <= m.pos <= start_finish + 3 for m in player.list_marble
        )

    def get_partner_index(self, player_idx: int) -> int:
        return (player_idx + 2) % self.state.cnt_player

    def get_active_and_partner_marbles(self) -> List[Marble]:
        active_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_idx]
        marbles = list(active_player.list_marble)
        if self.is_player_finished(active_idx):
            partner_idx = self.get_partner_index(active_idx)
            partner = self.state.list_player[partner_idx]
            marbles.extend(partner.list_marble)
        return marbles

    def get_active_and_partner_playerstates(self) -> List[PlayerState]:
        active_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_idx]
        if self.is_player_finished(active_idx):
            partner_idx = self.get_partner_index(active_idx)
            partner = self.state.list_player[partner_idx]
            return [active_player, partner]
        return [active_player]

    def _find_marble_by_pos(
        self, marbles: List[Marble], pos: int
    ) -> Optional[Marble]:
        return next((m for m in marbles if m.pos == pos), None)

    def get_list_action(self) -> List[Action]:
        actions: Set[Action] = set()
        active_player = self.state.list_player[self.state.idx_player_active]

        if not self.state.bool_card_exchanged and self.state.cnt_round == 0:
            for c in active_player.list_card:
                actions.add(Action(card=c, pos_from=None, pos_to=None))
            return list(actions)

        marbles_to_consider = self.get_active_and_partner_marbles()
        cards = active_player.list_card if not self.state.card_active else [
            self.state.card_active
        ]
        is_beginning_phase = all(
            marble.pos >= 64 for marble in active_player.list_marble
        )

        for card in cards:
            if card.rank == 'JKR':
                actions.update(
                    self._generate_joker_actions(
                        active_player, card, is_beginning_phase, marbles_to_consider
                    )
                )
            elif card.rank in ['A', 'K']:
                actions.update(
                    self._generate_start_card_actions(
                        active_player, card, marbles_to_consider
                    )
                )
            elif card.rank == 'J':
                actions.update(
                    self._generate_jack_card_actions(
                        active_player, card, marbles_to_consider
                    )
                )
            elif card.rank in {'2', '3', '5', '6', '8', '9', '10'}:
                actions.update(
                    self._generate_forward_move_actions(
                        active_player, card, marbles_to_consider
                    )
                )
        return list(actions)

    def _find_duplicate_actions(self, actions: List[Action]) -> None:
        action_counter = Counter(actions)
        duplicates = [
            action for action, count in action_counter.items() if count > 1
        ]
        if duplicates:
            print("Duplicate actions found:")
            for action in duplicates:
                print(action)
            raise ValueError("Duplicate actions detected in get_list_action.")

    def _generate_joker_actions(
        self, _active_player: PlayerState, card: Card,
        is_beginning_phase: bool, marbles_to_consider: List[Marble]
    ) -> List[Action]:
        actions = []
        for marble in marbles_to_consider:
            if marble.pos == 64:
                actions.append(
                    Action(card=card, pos_from=64, pos_to=0)
                )

        if is_beginning_phase:
            for suit in GameState.LIST_SUIT:
                for rank in ['A', 'K']:
                    actions.append(
                        Action(card=card, card_swap=Card(suit=suit, rank=rank))
                    )
        else:
            for suit in GameState.LIST_SUIT:
                for rank in GameState.LIST_RANK:
                    if rank != 'JKR':
                        actions.append(
                            Action(
                                card=card,
                                card_swap=Card(suit=suit, rank=rank)
                            )
                        )
        return actions


    def _generate_start_card_actions(
        self, _active_player: PlayerState, card: Card,
        marbles_to_consider: List[Marble]
    ) -> List[Action]:
        actions = []
        for marble in marbles_to_consider:
            if marble.pos == 64:
                actions.append(
                    Action(
                        card=card,
                        pos_from=64,
                        pos_to=0,
                        card_swap=None
                    )
                )

            if 0 <= marble.pos < 64:
                target_pos = marble.pos + 1
                if target_pos <= 63:
                    actions.append(
                        Action(
                            card=card,
                            pos_from=marble.pos,
                            pos_to=target_pos
                        )
                    )
        return actions

    def _generate_jack_card_actions(
        self, _active_player: PlayerState, card: Card,
        marbles_to_consider: List[Marble]
    ) -> List[Action]:
        actions = []
        found_valid_target = False

        # Check actions with opponent marbles
        for marble in marbles_to_consider:
            if marble.pos >= 64:  # Skip marbles already home
                continue
            for opponent in self.state.list_player:
                if opponent in self.get_active_and_partner_playerstates():
                    continue
                for opp_marble in opponent.list_marble:
                    if opp_marble.is_save or opp_marble.pos >= 64:
                        continue
                    # Valid target found
                    found_valid_target = True
                    actions.append(Action(
                        card=card, pos_from=marble.pos, pos_to=opp_marble.pos
                    ))
                    actions.append(Action(
                        card=card, pos_from=opp_marble.pos, pos_to=marble.pos
                    ))

        # If no valid targets, generate fallback actions
        if not found_valid_target:
            marbles_on_board = [m for m in marbles_to_consider if m.pos < 64]
            for i, marble_a in enumerate(marbles_on_board):
                for marble_b in marbles_on_board[i + 1:]:
                    actions.append(Action(
                        card=card, pos_from=marble_a.pos, pos_to=marble_b.pos
                    ))
                    actions.append(Action(
                        card=card, pos_from=marble_b.pos, pos_to=marble_a.pos
                    ))

        return actions


    def _generate_forward_move_actions(
        self, _active_player: PlayerState, card: Card,
        marbles_to_consider: List[Marble]
    ) -> List[Action]:
        actions = []
        forward_move_cards = {
            '2': 2, '3': 3, '5': 5, '6': 6, '8': 8, '9': 9, '10': 10
        }
        steps = forward_move_cards[card.rank]

        for marble in marbles_to_consider:
            if 0 <= marble.pos < 64:
                target_pos = marble.pos + steps
                if target_pos <= 63:
                    if not self.is_path_blocked(marble.pos, target_pos):
                        actions.append(
                            Action(
                                card=card,
                                pos_from=marble.pos,
                                pos_to=target_pos
                            )
                        )
        return actions

    def apply_action(self, action: Optional[Action]) -> None:
        self._ensure_cards_available()

        if not self.state.bool_card_exchanged and self.state.cnt_round == 0:
            active_player = self.state.list_player[self.state.idx_player_active]
            if action is None or action.card not in active_player.list_card:
                print(
                    "Invalid action: Card exchange requires choosing one of your cards."
                )
                return
            chosen_card = action.card
            active_player.list_card.remove(chosen_card)
            self.card_exchange_buffer[self.state.idx_player_active] = chosen_card
            self.state.idx_player_active = (
                self.state.idx_player_active + 1
            ) % self.state.cnt_player

            if all(c is not None for c in self.card_exchange_buffer):
                for i in range(self.state.cnt_player):
                    partner_idx = (i + 2) % self.state.cnt_player
                    # Safely cast to Card since all values are checked not to be None
                    card_to_add = cast(
                        Card, self.card_exchange_buffer[partner_idx]
                    )
                    self.state.list_player[i].list_card.append(card_to_add)
                self.card_exchange_buffer = [None, None, None, None]
                self.state.bool_card_exchanged = True
                self.state.idx_player_active = self.state.idx_player_started

            return

        if not self.state.list_card_draw:
            self.reshuffle_cards()

        active_player_idx = self.state.idx_player_active
        active_player = self.state.list_player[active_player_idx]

        marbles_to_consider = self.get_active_and_partner_marbles()

        if action is None:
            self._handle_no_action(active_player)
            return

        if action.card.rank == '7':
            self._handle_seven_card(action, active_player)
        elif action.card.rank == 'JKR':
            if action.card_swap:
                active_player.list_card.remove(action.card)
                self.state.card_active = action.card_swap
                print(
                    f"JOKER played: Active card is now {self.state.card_active}."
                )
                return
        elif action.card.rank == 'J':
            self._handle_jack_card_in_apply(
                action, active_player, marbles_to_consider
            )
        else:
            self._handle_normal_card_in_apply(
                action, active_player, marbles_to_consider
            )

        if self.steps_remaining is None:
            self._finalize_turn()

        self.check_and_handle_victory()

    def _ensure_cards_available(self) -> None:
        if not self.state.list_card_draw:
            self.reshuffle_cards()




    def check_and_handle_victory(self) -> None:
        """
        Checks for a winner and handles game state if victory is detected.
        """
        winner = self.check_victory()
        if winner:
            pass





    def _handle_jack_card_in_apply(
        self, action: Action, _active_player: PlayerState,
        marbles_to_consider: List[Marble]
    ) -> None:
        moving_marble = self._find_marble_by_pos(
            marbles_to_consider, action.pos_from
        ) if action.pos_from is not None else None

        opponent_marble = self._get_marble_at_position_of_opponent(
            action.pos_to
        ) if action.pos_to is not None else None

        if not opponent_marble and action.pos_to is not None:
            opponent_marble = next(
                (m for m in marbles_to_consider if m.pos == action.pos_to),
                None
            )

        if moving_marble and opponent_marble:
            moving_marble.pos, opponent_marble.pos = (
                opponent_marble.pos, moving_marble.pos
            )

    def _handle_normal_card_in_apply(
        self, action: Action, _active_player: PlayerState,
        marbles_to_consider: List[Marble]
    ) -> None:
        moving_marble = self._find_marble_by_pos(
            marbles_to_consider, action.pos_from
        ) if action.pos_from is not None else None

        if moving_marble:
            opponent_marble = self._get_marble_at_position_of_opponent(
                action.pos_to
            ) if action.pos_to is not None else None

            if not opponent_marble and action.pos_to is not None:
                partner_marble = next(
                    (
                        m for m in marbles_to_consider
                        if m.pos == action.pos_to and m != moving_marble
                    ),
                    None
                )
                if partner_marble:
                    opponent_marble = partner_marble

            if opponent_marble:
                self._send_marble_home(opponent_marble)

            if action.pos_to is not None:
                moving_marble.pos = action.pos_to
                moving_marble.is_save = True

    def reshuffle_cards(
        self, cards_per_player: Optional[int] = None
    ) -> None:
        total_cards_needed = (
            cards_per_player * self.state.cnt_player
            if cards_per_player else 0
        )

        while (
            cards_per_player and
            len(self.state.list_card_draw) < total_cards_needed
        ) or not self.state.list_card_draw:
            if self.state.list_card_discard:
                self.state.list_card_draw.extend(self.state.list_card_discard)
                self.state.list_card_discard.clear()
                random.shuffle(self.state.list_card_draw)
            else:
                self.state.list_card_draw = list(GameState.LIST_CARD)
                random.shuffle(self.state.list_card_draw)
                self.state.list_card_discard.clear()

        self._validate_card_count()

    def _validate_card_count(self) -> None:
        total_cards = (
            len(self.state.list_card_draw) +
            len(self.state.list_card_discard)
        )
        for player in self.state.list_player:
            total_cards += len(player.list_card)

    def _handle_no_action(self, active_player: PlayerState) -> None:
        print("No action provided; skipping turn or reshuffling cards.")
        if (
            self.state.card_active
            and self.state.card_active.rank == '7'
            and self.steps_remaining is not None
        ):
            self._restore_seven_card_backup()
            return

        if self.state.card_active and self.state.card_active.rank == '7':
            self._finalize_turn()
        else:
            self.fold_cards(active_player)

    def _handle_seven_card(
        self, action: Action, active_player: PlayerState
    ) -> None:
        if self.steps_remaining is None:
            self.steps_remaining = 7
            self.state.card_active = action.card
            self.seven_card_backup = self._create_seven_card_backup()

        steps_used = self._calculate_steps_used(action)
        if steps_used > self.steps_remaining:
            raise ValueError("Exceeded remaining steps for SEVEN.")

        moving_marble = self._get_marble_at_position(
            active_player, action.pos_from
        ) if action.pos_from is not None else None

        if moving_marble and action.pos_to is not None:
            self._handle_intermediate_positions(
                action, moving_marble, active_player
            )
            moving_marble.pos = action.pos_to
            self.steps_remaining -= steps_used

            if self.steps_remaining == 0:
                self.steps_remaining = None
                self.state.card_active = None
                active_player.list_card.remove(action.card)
                self.seven_card_backup = None

    def _handle_joker_card(
        self, action: Action, active_player: PlayerState
    ) -> None:
        if action.card_swap:
            self.state.card_active = action.card_swap
            active_player.list_card.remove(action.card)

    def _handle_jack_card(
        self, action: Action, active_player: PlayerState
    ) -> None:
        moving_marble = self._get_marble_at_position(
            active_player, action.pos_from
        ) if action.pos_from is not None else None

        opponent_marble = self._get_marble_at_position_of_opponent(
            action.pos_to
        ) if action.pos_to is not None else None

        if moving_marble and opponent_marble:
            moving_marble.pos, opponent_marble.pos = (
                opponent_marble.pos, moving_marble.pos
            )

    def _handle_normal_card(
        self, action: Action, active_player: PlayerState
    ) -> None:
        moving_marble = self._get_marble_at_position(
            active_player, action.pos_from
        ) if action.pos_from is not None else None

        if moving_marble and action.pos_to is not None:
            opponent_marble = self._get_marble_at_position_of_opponent(
                action.pos_to
            )
            if opponent_marble:
                self._send_marble_home(opponent_marble)
            moving_marble.pos = action.pos_to
            moving_marble.is_save = True

    def _finalize_turn(self) -> None:
        self.state.card_active = None
        self.state.idx_player_active = (
            self.state.idx_player_active + 1
        ) % self.state.cnt_player

        if self.state.idx_player_active == self.state.idx_player_started:
            self._handle_round_completion()

    def start_new_round(self) -> None:
        self._handle_round_completion()
        print(f"Round {self.state.cnt_round} started.")

    def _calculate_steps_used(self, action: Action) -> int:
        pos_from = action.pos_from
        pos_to = action.pos_to
        player_idx = self.state.idx_player_active
        start_pos = 16 * player_idx
        finish_start = 68 + 8 * player_idx

        if pos_from is None or pos_to is None:
            return 0

        if pos_from < 64 and pos_to < 64:
            return (pos_to - pos_from) % 64

        if pos_from < 64 and pos_to >= finish_start:
            steps_on_board = (start_pos - pos_from) % 64
            steps_in_finish = (pos_to - finish_start) + 1
            return steps_on_board + steps_in_finish

        if pos_from >= 64 and pos_to >= 64:
            return abs(pos_to - pos_from)

        return abs(pos_to - pos_from)


    def _handle_intermediate_positions(
        self, action: Action, moving_marble: Marble,
        active_player: PlayerState
    ) -> None:
        if action.pos_from is not None and action.pos_to is not None:
            for pos in range(action.pos_from + 1, action.pos_to + 1):
                opponent_marble = self._get_marble_at_position_of_opponent(pos)
                if opponent_marble:
                    self._send_marble_home(opponent_marble)
                    break

                own_marble = self._get_marble_at_position(
                    active_player, pos
                )
                if own_marble and own_marble != moving_marble:
                    self._send_marble_home(own_marble)
                    break

    def _get_marble_at_position(
        self, player: PlayerState, position: int
    ) -> Optional[Marble]:
        return next(
            (m for m in player.list_marble if m.pos == position),
            None
        )

    def _get_marble_at_position_of_opponent(
        self, position: Optional[int]
    ) -> Optional[Marble]:
        if position is None:
            return None
        for player in self.state.list_player:
            for marble in player.list_marble:
                if marble.pos == position:
                    return marble
        return None



    def _handle_round_completion(self) -> None:
        self.state.cnt_round += 1
        self.state.bool_card_exchanged = False
        self.state.idx_player_started = (self.state.idx_player_started + 1) % self.state.cnt_player
        cards_per_player = self._calculate_cards_per_round()

        self.reshuffle_cards(cards_per_player)
        self._deal_cards(cards_per_player)
        print(f"Round {self.state.cnt_round} started with {cards_per_player} cards per player.")

    def _calculate_cards_per_round(self) -> int:
        if 1 <= self.state.cnt_round <= 5:
            return 7 - self.state.cnt_round
        return 7 - ((self.state.cnt_round - 1) % 5 + 1)

    def _deal_cards(self, cards_per_player: int) -> None:
        self.reshuffle_cards(cards_per_player)
        draw_pile = self.state.list_card_draw
        for player in self.state.list_player:
            for _ in range(cards_per_player):
                if not draw_pile:
                    self.reshuffle_cards(cards_per_player)
                card = draw_pile.pop()
                player.list_card.append(card)
        self.state.list_card_draw = draw_pile

    def check_victory(self) -> Optional[str]:
        if self.state.phase == GamePhase.FINISHED:
            return "Game already finished"

        for player in self.state.list_player:
            if all(76 <= marble.pos <= 95 for marble in player.list_marble):
                self.state.phase = GamePhase.FINISHED
                return f"Player {player.name} has won!"

        return None


    def get_player_view(self, idx_player: int) -> GameState:
        masked_players: List[PlayerState] = []
        for idx, player in enumerate(self.state.list_player):
            if idx == idx_player:
                masked_players.append(player)
            else:
                masked_players.append(
                    PlayerState(
                        name=player.name,
                        list_card=[],
                        list_marble=player.list_marble,
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
            list_card_draw=[],
            list_card_discard=[],
            card_active=self.state.card_active,
        )

    def _create_seven_card_backup(self) -> Dict[str, Any]:
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

    def _restore_seven_card_backup(self) -> None:
        if not self.seven_card_backup:
            return
        for player_idx, card_list in self.seven_card_backup['card_hands']:
            self.state.list_player[player_idx].list_card = card_list
        for player_idx, marble_idx, pos, is_save in self.seven_card_backup['marbles']:
            self.state.list_player[player_idx].list_marble[marble_idx].pos = pos
            self.state.list_player[player_idx].list_marble[marble_idx].is_save = is_save
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
    game.start_new_round()
    game.print_state()
    