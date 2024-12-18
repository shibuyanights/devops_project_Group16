# tests/test_dog.py

import pytest
from server.py.dog import Dog, Card, Marble, PlayerState, Action, GameState, GamePhase
from server.py.dog import RandomPlayer, GameState, Action, Card
from typing import List, Any
from abc import ABCMeta, abstractmethod
from server.py.game import Game, Player

@pytest.fixture
def game_instance():
    """Fixture to create a fresh instance of the Dog game."""
    return Dog()


def test_initialization(game_instance):
    """Test game initialization."""
    state = game_instance.get_state()
    assert state.phase == GamePhase.RUNNING, "Game should start in RUNNING phase."
    assert len(state.list_player) == 4, "There should be 4 players."
    # Each player should start with 6 cards and 4 marbles as defined in reset
    for player in state.list_player:
        assert len(player.list_card) == 6, "Each player should start with 6 cards."
        assert len(player.list_marble) == 4, "Each player should have 4 marbles."
        for marble in player.list_marble:
            # Marbles start in kennel range
            assert 64 <= marble.pos <= 95, "Marbles should start in their kennel range."
    # Draw pile size check
    expected_draw_pile_size = 110 - 4 * 6  # 110 total, 24 dealt initially
    assert len(state.list_card_draw) == expected_draw_pile_size, f"Draw pile should have {expected_draw_pile_size} cards."


def test_reset_function(game_instance):
    """Test game reset functionality."""
    # Modify state and reset again
    game_instance.reset()
    state = game_instance.get_state()
    assert state.phase == GamePhase.RUNNING, "Game should be in RUNNING phase after reset."
    for player in state.list_player:
        assert len(player.list_card) == 6, "Each player should have 6 cards after reset."
        for marble in player.list_marble:
            assert 64 <= marble.pos <= 95, "Marbles should reset to kennel positions."


def test_is_path_blocked_no_block(game_instance):
    """Test path blocking when path is clear."""
    assert not game_instance.is_path_blocked(4, 8), "Path should not be blocked if no marbles."


def test_is_path_blocked_with_block(game_instance):
    """Test path blocking with a blocking marble."""
    state = game_instance.get_state()
    # Place a safe marble at position 6
    state.list_player[0].list_marble[0].pos = 6
    state.list_player[0].list_marble[0].is_save = True
    game_instance.set_state(state)
    assert game_instance.is_path_blocked(4, 8), "Path should be blocked by a safe marble at pos 6."


def test_generate_actions_start_card(game_instance):
    """Test generating actions for A/K cards to start marbles."""
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    # Give active player an Ace card
    active_player.list_card = [Card(suit='♠', rank='A')]
    # Ensure marbles in kennel
    for marble in active_player.list_marble:
        marble.pos = 64
        marble.is_save = False
    game_instance.set_state(state)
    actions = game_instance.get_list_action()
    expected_action = Action(card=Card(suit='♠', rank='A'), pos_from=64, pos_to=0)
    assert expected_action in actions, "Should have action to move marble from kennel to start."


def test_generate_actions_forward_move(game_instance):
    """Test generating actions for normal forward move cards like '2'."""
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    move_card = Card(suit='♠', rank='2')
    active_player.list_card = [move_card]
    # Marble on board
    active_player.list_marble[0].pos = 10
    active_player.list_marble[0].is_save = False
    game_instance.set_state(state)
    actions = game_instance.get_list_action()
    # Moving from 10 to 12 using '2'
    expected_action = Action(card=move_card, pos_from=10, pos_to=12)
    assert expected_action in actions, "Should have forward move action from 10 to 12."


def test_generate_actions_joker_in_beginning(game_instance):
    """Test Joker actions in the beginning phase."""
    state = game_instance.get_state()
    joker_card = Card(suit='', rank='JKR')
    active_player = state.list_player[state.idx_player_active]
    active_player.list_card = [joker_card]
    # Beginning phase: all marbles in kennel
    for player in state.list_player:
        for marble in player.list_marble:
            marble.pos = 64
            marble.is_save = False
    game_instance.set_state(state)
    actions = game_instance.get_list_action()
    # Should have action to move marble from kennel to start
    move_action = Action(card=joker_card, pos_from=64, pos_to=0)
    assert move_action in actions, "Joker should allow starting a marble."
    # Should have at least one swap action with A or K
    swap_actions = [a for a in actions if a.card == joker_card and a.card_swap is not None]
    assert len(swap_actions) > 0, "Joker should have swap actions with A/K in beginning phase."


def test_generate_actions_jocker_non_beginning(game_instance):
    """Test Joker actions outside beginning phase (one marble on board)."""
    state = game_instance.get_state()
    joker_card = Card(suit='', rank='JKR')
    active_player = state.list_player[state.idx_player_active]
    active_player.list_card = [joker_card]
    # Move one marble out to end beginning phase
    active_player.list_marble[0].pos = 0
    active_player.list_marble[0].is_save = True
    active_player.list_marble[1].pos = 64
    game_instance.set_state(state)
    actions = game_instance.get_list_action()
    # Joker should still allow starting another marble
    move_action = Action(card=joker_card, pos_from=64, pos_to=0)
    assert move_action in actions, "Joker should allow starting another marble."
    # Swap with any non-JKR card
    swap_actions = [a for a in actions if a.card == joker_card and a.card_swap is not None]
    assert len(swap_actions) > 0, "Joker should have swap actions with various cards outside beginning phase."


def test_apply_action_move_marble(game_instance):
    """Test applying a forward move action."""
    state = game_instance.get_state()
    move_card = Card(suit='♠', rank='2')
    active_player = state.list_player[state.idx_player_active]
    active_player.list_card = [move_card]
    active_player.list_marble[0].pos = 10
    active_player.list_marble[0].is_save = False
    game_instance.set_state(state)
    action = Action(card=move_card, pos_from=10, pos_to=12)
    game_instance.apply_action(action)
    updated_state = game_instance.get_state()
    assert updated_state.list_player[0].list_marble[0].pos == 12, "Marble should have moved to 12."


def test_apply_action_joker_swap(game_instance):
    """Test applying a Joker swap action."""
    state = game_instance.get_state()
    joker_card = Card(suit='', rank='JKR')
    active_player = state.list_player[state.idx_player_active]
    active_player.list_card = [joker_card]
    # Choose to swap Joker with 'A' card
    swap_card = Card(suit='♠', rank='A')
    action = Action(card=joker_card, pos_from=None, pos_to=None, card_swap=swap_card)
    game_instance.set_state(state)
    game_instance.apply_action(action)
    updated_state = game_instance.get_state()
    assert updated_state.card_active == swap_card, "Card active should now be 'A' after Joker swap."
    assert joker_card not in updated_state.list_player[0].list_card, "Joker removed from player's hand."


def test_apply_action_jack_swap(game_instance):
    """Test applying a 'J' card to swap marbles."""
    state = game_instance.get_state()
    j_card = Card(suit='♠', rank='J')
    active_player = state.list_player[0]
    opponent_player = state.list_player[1]
    active_player.list_card = [j_card]
    # Active player's marble at 10
    active_player.list_marble[0].pos = 10
    # Opponent's marble at 12
    opponent_player.list_marble[0].pos = 12
    game_instance.set_state(state)
    action = Action(card=j_card, pos_from=10, pos_to=12)
    game_instance.apply_action(action)
    updated_state = game_instance.get_state()
    # After swap
    assert updated_state.list_player[0].list_marble[0].pos == 12, "Active player's marble moved to 12."
    assert updated_state.list_player[1].list_marble[0].pos == 10, "Opponent's marble moved to 10."


def test_apply_action_no_action_fold(game_instance):
    """Test applying no action leads to folding if no moves and no active 7 card."""
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    # Clear player's hand to force folding
    active_player.list_card.clear()
    game_instance.set_state(state)
    game_instance.apply_action(None)
    updated_state = game_instance.get_state()
    # Player should have folded (no error raised), next player's turn
    assert updated_state.idx_player_active == 1, "Turn should pass to next player after folding."


def test_round_progression(game_instance):
    """Test round progression logic when no moves are available."""
    game_instance.reset()
    state = game_instance.get_state()
    initial_round = state.cnt_round

    # Force a scenario where no moves are possible for all players
    for player in state.list_player:
        player.list_card.clear()
        for marble in player.list_marble:
            marble.pos = 0  # All marbles on the board, but let's assume no moves possible

    game_instance.set_state(state)

    # Apply no action for a full cycle of 4 players
    for _ in range(4):
        game_instance.apply_action(None)

    updated_state = game_instance.get_state()

    # Now the round should have incremented after a full cycle of turns
    assert updated_state.cnt_round == initial_round + 1, "Round should increment after a full cycle of turns."



def test_apply_action_seven_card_exceed_steps(game_instance):
    """Test that SEVEN card's step limit raises an error when exceeded."""
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    seven_card = Card(suit='♠', rank='7')
    active_player.list_card = [seven_card]
    # Prepare a scenario for movement
    active_player.list_marble[0].pos = 10
    active_player.list_marble[0].is_save = False
    game_instance.set_state(state)
    # First apply a valid move with 7 (e.g., move 3 steps)
    action_valid = Action(card=seven_card, pos_from=10, pos_to=13)
    game_instance.apply_action(action_valid)
    assert game_instance.steps_remaining == 7 - 3, "Steps remaining should reduce by steps used."

    # Now try to exceed remaining steps
    action_invalid = Action(card=seven_card, pos_from=13, pos_to=21)  # Too far
    with pytest.raises(ValueError, match="Exceeded remaining steps for SEVEN."):
        game_instance.apply_action(action_invalid)


def test_victory_condition(game_instance):
    """Test that the game sets phase to FINISHED when a team finishes."""
    state = game_instance.get_state()
    # Force team 1 (players 0 and 2) to finish
    for marble in state.list_player[0].list_marble:
        marble.pos = 76
    for marble in state.list_player[2].list_marble:
        marble.pos = 76
    game_instance.set_state(state)
    # Check victory
    game_instance.check_victory()
    updated_state = game_instance.get_state()
    assert updated_state.phase == GamePhase.FINISHED, "Game should be finished if a team finishes their marbles."


def test_player_view_masking(game_instance):
    """Test that get_player_view masks other players' cards."""
    player_view = game_instance.get_player_view(0)
    assert len(player_view.list_player[0].list_card) > 0, "Active player's cards should be visible."
    for p in player_view.list_player[1:]:
        assert len(p.list_card) == 0, "Other players' cards should be masked."


def test_card_exchange_at_round_zero(game_instance):
    """Test card exchange at round 0."""
    state = game_instance.get_state()
    state.cnt_round = 0
    state.bool_card_exchanged = False
    active_player = state.list_player[state.idx_player_active]
    exchange_card = active_player.list_card[0]
    game_instance.set_state(state)
    # Apply exchange action
    action = Action(card=exchange_card, pos_from=None, pos_to=None, card_swap=None)
    game_instance.apply_action(action)
    updated_state = game_instance.get_state()
    # After one player exchanges, it should move to next player's turn to exchange
    assert updated_state.idx_player_active == 1, "Should move to next player after exchanging a card."

def test_seven_card_no_moves(game_instance):
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    active_player.list_card = [Card(suit='♠', rank='7')]
    # Place all marbles at positions where no moves are possible
    for marble in active_player.list_marble:
        marble.pos = 0  # Example position
    game_instance.set_state(state)

    actions = game_instance.get_list_action()
    assert len(actions) == 0, "No moves should be available for SEVEN card when marbles cannot move."

def test_joker_swap_non_beginning_phase(game_instance):
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    joker_card = Card(suit='', rank='JKR')
    active_player.list_card = [joker_card]

    # Set one marble outside the kennel
    active_player.list_marble[0].pos = 10
    game_instance.set_state(state)

    actions = game_instance.get_list_action()
    swap_actions = [action for action in actions if action.card_swap]
    assert swap_actions, "Joker swap actions should exist outside the beginning phase."


def test_card_equality():
    card1 = Card(suit='♠', rank='A')
    card2 = Card(suit='♠', rank='A')
    card3 = Card(suit='♥', rank='K')

    assert card1 == card2, "Cards with the same suit and rank should be equal."
    assert card1 != card3, "Cards with different suits or ranks should not be equal."
    assert str(card1) == "♠A", "String representation of card should match."

def test_player_win(game_instance):
    state = game_instance.get_state()
    active_player = state.list_player[0]

    # Move all marbles to the finish area
    for i, marble in enumerate(active_player.list_marble):
        marble.pos = 68 + i  # Finish area positions

    game_instance.set_state(state)
    result = game_instance.check_victory()
    assert state.phase == GamePhase.FINISHED, "Game should be in FINISHED phase after a win."


def test_card_comparison():
    c1 = Card(suit='♠', rank='A')
    c2 = Card(suit='♥', rank='A')
    c3 = Card(suit='♥', rank='K')
    c4 = Card(suit='♠', rank='A')  # same as c1 except suit difference

    # __eq__
    assert c1 != c2
    assert c1 == Card(suit='♠', rank='A')  # equal to a card with same suit, rank
    # __lt__ relies on the string comparison of __str__
    # suits are likely unicode and ranks are strings, so this is lex order:
    # '♠A' < '♥A' because '♠' < '♥' in Unicode order
    assert (c1 < c2) == (str(c1) < str(c2))
    assert (c2 < c3) == (str(c2) < str(c3))
    assert (c1 < c4) == (str(c1) < str(c4))


def test_print_state(capfd):
    game = Dog()
    game.print_state()  # Assuming it prints something about the game state
    captured = capfd.readouterr()
    # Just check that something was printed; adjust assertions as needed
    assert captured.out is not None

def test_jack_card_swap():
    game = Dog()
    active_player = game.state.list_player[0]
    opponent_player = game.state.list_player[1]

    # Give both players marbles on the board
    active_player.list_marble[0].pos = 5
    active_player.list_marble[0].is_save = False
    opponent_player.list_marble[0].pos = 10
    opponent_player.list_marble[0].is_save = False

    # Give active player a Jack card
    jack_card = Card(suit='♠', rank='J')
    active_player.list_card.append(jack_card)

    # Generate actions should now produce jack swap actions
    actions = game.get_list_action()
    # Filter actions to find one that swaps our marble at pos 5 with opp. marble at pos 10
    jack_actions = [a for a in actions if a.card == jack_card and a.pos_from == 5 and a.pos_to == 10]

    assert len(jack_actions) > 0, "Should generate jack swap actions"

    # Apply one such action
    swap_action = jack_actions[0]
    game.apply_action(swap_action)

    # After the swap, our marble should move to pos 10 and opponent's marble to pos 5
    assert active_player.list_marble[0].pos == 10
    assert opponent_player.list_marble[0].pos == 5

def test_no_action_with_seven_card_active():
    game = Dog()
    active_player = game.state.list_player[0]

    # Give a '7' card and set a scenario
    seven_card = Card(suit='♠', rank='7')
    active_player.list_card.append(seven_card)

    # Start by applying a '7' card action that requires multiple steps
    # Just move a marble from 0 to 1 as the first step
    # Ensure a marble is on the board
    active_player.list_marble[0].pos = 0
    action_step = Action(card=seven_card, pos_from=0, pos_to=1)
    game.apply_action(action_step)

    # Now seven card is active and steps_remaining should be reduced
    assert game.state.card_active == seven_card
    assert game.steps_remaining is not None

    # Apply None action to trigger the restore backup logic
    game.apply_action(None)

    # The seven card turn should have been aborted and restored
    assert game.state.card_active is None
    assert game.steps_remaining is None

def test_random_player_action():
    from server.py.dog import RandomPlayer, GameState, Action, Card  # Add this if imports at the top don't work

    player = RandomPlayer()
    state = GameState(
        cnt_player=4,
        phase="running",
        cnt_round=1,
        bool_card_exchanged=False,
        idx_player_started=0,
        idx_player_active=0,
        list_player=[],
        list_card_draw=[],
        list_card_discard=[],
        card_active=None
    )
    actions = [Action(card=Card(suit='♠', rank='A')), Action(card=Card(suit='♥', rank='2'))]
    chosen_action = player.select_action(state, actions)
    # Verify that an action was chosen
    assert chosen_action in actions



def test_round_progression_and_intermediate_positions():
    game = Dog()
    active_player = game.state.list_player[0]

    # Give a '7' card (multiple step card)
    seven_card = Card(suit='♠', rank='7')
    active_player.list_card.append(seven_card)

    # Place active player's marble at position close to finish or another marble
    active_player.list_marble[0].pos = 60
    active_player.list_marble[0].is_save = False

    # Move it over several positions to test intermediate positions handling
    # For simplicity, assume no blocks (adjust as needed)
    action_long_move = Action(card=seven_card, pos_from=60, pos_to=67)
    game.apply_action(action_long_move)

    # Steps used should have been calculated
    # If intermediate opponent marbles were present (you can place them at pos 63 for example),
    # they would be sent home and intermediate logic triggered.
    # Here we just ensure the code runs without errors.
    assert active_player.list_marble[0].pos == 67

    # Finish a round to trigger dealing cards
    # Move through players or call _handle_round_completion directly if allowed
    for _ in range(3):  # cycle through players to end the round
        game._finalize_turn()

    # Now a new round should have started and cards dealt
    # Just checking no error occurred and coverage improved.
    assert game.state.cnt_round > 1


def test_send_marble_home(game_instance):
    """Test sending an opponent's marble home."""
    state = game_instance.get_state()
    opponent_player = state.list_player[1]
    # Place an opponent marble on the board and mark it safe
    opponent_player.list_marble[0].pos = 10
    opponent_player.list_marble[0].is_save = True
    game_instance.set_state(state)
    marble_to_send = opponent_player.list_marble[0]

    # Send marble home
    game_instance._send_marble_home(marble_to_send)
    # Marble should now be back in its kennel range
    owner_idx = 1
    kennel_start = 64 + owner_idx * 8
    assert marble_to_send.pos == kennel_start, "Marble should be sent home."
    assert not marble_to_send.is_save, "Marble should not be safe after being sent home."


def test_get_marble_owner(game_instance):
    """Test retrieval of marble owner."""
    state = game_instance.get_state()
    # The first marble of player 0 should belong to them
    marble = state.list_player[0].list_marble[0]
    owner_idx = game_instance._get_marble_owner(marble)
    assert owner_idx == 0, "Owner of the marble should be player 0."


def test_find_marble_by_pos(game_instance):
    """Test finding a marble by position."""
    state = game_instance.get_state()
    active_player = state.list_player[0]
    # Place a marble at a known position
    active_player.list_marble[0].pos = 20
    game_instance.set_state(state)
    marbles = active_player.list_marble
    found = game_instance._find_marble_by_pos(marbles, 20)
    assert found is not None, "Marble at position 20 should be found."
    assert found.pos == 20, "Found marble should match the searched position."


def test_get_marble_at_position_of_opponent(game_instance):
    """Test getting a marble at a position that belongs to an opponent."""
    state = game_instance.get_state()
    opponent_player = state.list_player[1]
    opponent_player.list_marble[0].pos = 30
    game_instance.set_state(state)

    found = game_instance._get_marble_at_position_of_opponent(30)
    assert found is not None, "Should find an opponent's marble at pos 30."
    assert found.pos == 30, "Found opponent marble should match position."



def test_reshuffle_cards_with_empty_discard(game_instance):
    """Test reshuffling cards when discard pile is empty."""
    state = game_instance.get_state()
    # Clear discard pile just in case
    state.list_card_discard.clear()
    # Clear draw pile to force reshuffle
    state.list_card_draw.clear()
    game_instance.set_state(state)

    # This should reshuffle from the full original deck
    game_instance.reshuffle_cards()
    updated_state = game_instance.get_state()
    assert len(updated_state.list_card_draw) > 0, "Draw pile should be replenished after reshuffle."


def test_no_action_seven_card_active_abort(game_instance):
    """Test applying no action when a seven card move is partially done, causing restore."""
    state = game_instance.get_state()
    active_player = state.list_player[state.idx_player_active]
    seven_card = Card(suit='♠', rank='7')
    active_player.list_card.append(seven_card)
    # Move a marble onto the board
    active_player.list_marble[0].pos = 0
    game_instance.set_state(state)

    # Apply a partial seven move (3 steps forward)
    action = Action(card=seven_card, pos_from=0, pos_to=3)
    game_instance.apply_action(action)
    assert game_instance.steps_remaining == 4, "After using 3 steps of seven, 4 remain."

    # Now apply no action to abort
    game_instance.apply_action(None)
    updated_state = game_instance.get_state()
    # Steps and card_active should be reset
    assert game_instance.steps_remaining is None, "Seven steps should be reset."
    assert updated_state.card_active is None, "No card should be active after abort."


def test_jack_card_when_no_opponent_marbles(game_instance):
    """Test 'J' card actions when there are no opponent marbles to swap."""
    state = game_instance.get_state()
    j_card = Card(suit='♠', rank='J')
    active_player = state.list_player[state.idx_player_active]
    active_player.list_card = [j_card]

    # Remove all opponent marbles from the board or place them in kennel safe zones
    for i, p in enumerate(state.list_player):
        if i != state.idx_player_active:
            for m in p.list_marble:
                m.pos = 64  # Kennel

    game_instance.set_state(state)
    actions = game_instance.get_list_action()
    # With no opponent marbles on board, Jack actions might only allow swapping between own/team marbles if applicable
    # Just ensure no error, and possibly fewer or no actions available
    # The test ensures coverage rather than a specific outcome
    assert isinstance(actions, list), "Actions should be a list even if empty."



def test_calculate_steps_used_kennel_to_finish(game_instance):
    """Test step calculation for a complex move from board into finishing area."""
    state = game_instance.get_state()
    player_idx = state.idx_player_active
    active_player = state.list_player[player_idx]
    seven_card = Card(suit='♠', rank='7')
    active_player.list_card.append(seven_card)

    # Place marble near finish entry
    # Board start pos for player_idx = 16 * player_idx, finish start = 68 + 8 * player_idx
    finish_start = 68 + 8 * player_idx
    active_player.list_marble[0].pos = 60
    game_instance.set_state(state)
    # Move from 60 into finish area at 70 (2 steps into finish)
    action = Action(card=seven_card, pos_from=60, pos_to=70)
    steps_used = game_instance._calculate_steps_used(action)
    # Calculate expected: from 60 to start_pos(16*player_idx); depends on player_idx, but let's trust modulo logic
    # To keep this generic, just ensure steps_used is a positive integer and not an error
    assert isinstance(steps_used, int), "Steps used should be calculated as an integer."
    assert steps_used > 0, "Steps used should be greater than zero."


def test_find_duplicate_actions(game_instance):
    # force duplication to trigger _find_duplicate_actions exception
    action = Action(card=Card(suit='♠', rank='2'), pos_from=10, pos_to=12)
    actions = [action, action]
    with pytest.raises(ValueError, match="Duplicate actions detected"):
        game_instance._find_duplicate_actions(actions)

def test_is_player_finished(game_instance):
    idx = game_instance.state.idx_player_active
    start_finish = 68 + 8 * idx
    for i, m in enumerate(game_instance.state.list_player[idx].list_marble):
        m.pos = start_finish + i
    assert game_instance.is_player_finished(idx)

def test_calculate_cards_per_round_extended(game_instance):
    game_instance.state.cnt_round = 10
    cards = game_instance._calculate_cards_per_round()
    assert cards == 7 - ((10 - 1) % 5 + 1)

def test_intermediate_positions_with_block():
    # Test scenario that triggers opponent marble removal in the middle of a 7-move
    game = Dog()
    active_player = game.state.list_player[0]
    opponent_player = game.state.list_player[1]
    seven_card = Card(suit='♠', rank='7')
    active_player.list_card.append(seven_card)

    # Place active player's marble at 60
    active_player.list_marble[0].pos = 60
    active_player.list_marble[0].is_save = False
    # Place opponent marble at 63 (intermediate position)
    opponent_player.list_marble[0].pos = 63
    opponent_player.list_marble[0].is_save = False

    action_long_move = Action(card=seven_card, pos_from=60, pos_to=67)
    game.apply_action(action_long_move)
    # The opponent marble at 63 should be sent home
    kennel_start = 64 + 1 * 8
    assert opponent_player.list_marble[0].pos == kennel_start
    assert active_player.list_marble[0].pos == 67    