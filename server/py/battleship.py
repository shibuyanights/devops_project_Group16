from typing import List, Optional, Dict
import random
import string
from enum import Enum
from pydantic import BaseModel
from colorama import init, Fore, Back, Style # type: ignore
from server.py.game import Game, Player

init(convert=True)


class ActionType(str, Enum):
    SET_SHIP = 'set_ship'
    SHOOT = 'shoot'


class BattleshipAction(BaseModel):
    action_type: ActionType
    ship_name: Optional[str] = None
    location: List[str]


class Ship(BaseModel):
    name: str
    length: int
    location: Optional[List[str]] = None



class PlayerState(BaseModel):
    name: str
    ships: List[Ship] = [
        Ship(name="carrier", length=5),
        Ship(name="battleship", length=4),
        Ship(name="cruiser", length=3),
        Ship(name="submarine", length=3),
        Ship(name="destroyer", length=2),
    ]
    shots: List[str] = []
    successful_shots: List[str] = []



class GamePhase(str, Enum):
    SETUP = 'setup'
    RUNNING = 'running'
    FINISHED = 'finished'


class BattleshipGameState(BaseModel):
    idx_player_active: int = random.choice([0, 1])
    phase: GamePhase = GamePhase.SETUP
    winner: Optional[int] = None
    players: List[PlayerState] = [PlayerState(name='Player1'), PlayerState(name='Player2')]

    def all_ships_located(self) -> bool:
        for ship in self.players[self.idx_player_active].ships:
            if ship.location is None:
                return False
        return True

    def get_player_ships(self, active_player: bool) -> List[Ship]:
        if active_player:
            idx_player = self.idx_player_active
        else:
            idx_player = (self.idx_player_active + 1) % 2
        return self.players[idx_player].ships

    def get_player_shots(self, active_player: bool) -> List[str]:
        if active_player:
            idx_player = self.idx_player_active
        else:
            idx_player = (self.idx_player_active + 1) % 2
        return self.players[idx_player].shots

    def check_if_finished(self) -> bool:
        # Does the opponent player still have some ships left?
        if not self.all_ships_located():
            return False
        shots = set(self.players[self.idx_player_active].shots)
        for ship in self.players[(self.idx_player_active + 1) % 2].ships:
            if ship.location is not None:
                if len(set(ship.location).difference(shots)) > 0:
                    return False
        return True

    def apply_action(self, action: BattleshipAction) -> None:
        if action.action_type == 'set_ship':
            existing_ship = False
            for ship in self.get_player_ships(active_player=True):
                if ship.name == action.ship_name:
                    ship.location = action.location.copy()
                    existing_ship = True
                    break
            if not existing_ship:
                new_ship = Ship(
                    name=action.ship_name if action.ship_name is not None else 'ship',
                    length=len(action.location),
                    location=action.location)
                self.get_player_ships(active_player=True).append(new_ship)
            # test if both player have set all ship locations -> phase = running
            all_ships_located = True
            for player in self.players:
                for ship in player.ships:
                    all_ships_located = all_ships_located and ship.location is not None
                if len(player.ships) < 5:
                    all_ships_located = False
            if all_ships_located:
                self.phase = GamePhase.RUNNING
        else:
            self.players[self.idx_player_active].shots.extend(action.location)
            opponent_ship_locations = [
                loc for ship in self.get_player_ships(False) if ship.location is not None for loc in ship.location]
            if action.location[0] in opponent_ship_locations:
                self.players[self.idx_player_active].successful_shots.extend(action.location)
        if self.check_if_finished():
            self.phase = GamePhase.FINISHED
            self.winner = self.idx_player_active
        else:
            self.idx_player_active = (self.idx_player_active + 1) % 2

    def get_masked_state(self, idx_player: int) -> "BattleshipGameState":
        other_player = (idx_player + 1) % 2
        masked_state = BattleshipGameState()
        masked_state.idx_player_active = self.idx_player_active
        masked_state.winner = self.winner
        masked_state.phase = self.phase
        masked_state.players[idx_player] = self.players[idx_player]
        masked_state.players[other_player].shots = self.players[other_player].shots
        masked_state.players[other_player].successful_shots = self.players[other_player].successful_shots

        # show ships that were sunk
        masked_state.players[other_player].ships = []
        for ship in self.players[other_player].ships:
            if ship.location is not None:
                cnt = 0
                for shot in self.players[idx_player].successful_shots:
                    if shot in ship.location:
                        cnt += 1
                if cnt == len(ship.location):
                    masked_state.players[other_player].ships.append(ship)

        return masked_state


def get_possible_locations(ship_length: int, board_size: int) -> List[List[str]]:
    if ship_length < 1:
        raise ValueError('Ship length has to be positive')
    if ship_length > board_size:
        raise ValueError(f"Ship of length {ship_length} is too large for board size {board_size}")
    x_names = list(string.ascii_uppercase)[:board_size]
    y_names = [str(y) for y in range(1, board_size + 1)]
    options = []
    # horizontal locations
    for x_pos in range(board_size - ship_length + 1):
        h_locations = [x_names[idx] for idx in range(x_pos, x_pos + ship_length)]
        options.extend([[x_name + y_name for x_name in h_locations] for y_name in y_names])

    if ship_length > 1:
        # vertical locations
        for y_pos in range(board_size - ship_length + 1):
            v_locations = [y_names[idx] for idx in range(y_pos, y_pos + ship_length)]
            options.extend([[x_name + y_name for y_name in v_locations] for x_name in x_names])
    return options


def print_player_board(ships: List[Ship], enemy_shots: List[str], board_size: int = 10) -> None:
    x_coords = list(string.ascii_uppercase)[:board_size]
    y_coords = [str(y) for y in range(1, board_size + 1)]
    print("   " + "  ".join(x_coords) + " ")
    ship_locations = [loc for ship in ships if ship.location is not None for loc in ship.location]
    for y_coord in y_coords:
        y_string = f"{y_coord:>2}"
        for x_coord in x_coords:
            coordinate = x_coord + y_coord
            if coordinate in ship_locations:
                if coordinate in enemy_shots:
                    y_string += Fore.RED + Back.WHITE + Style.BRIGHT + " X " + Style.RESET_ALL
                else:
                    y_string += Back.WHITE + " S " + Style.RESET_ALL
            else:
                if coordinate in enemy_shots:
                    y_string += Fore.CYAN + " O " + Style.RESET_ALL
                else:
                    y_string += " - "
        print(y_string)


class Battleship(Game):

    def __init__(self) -> None:
        self.state = BattleshipGameState()
        self.ship_locations: Dict[int, List[List[str]]] = {
            2: get_possible_locations(2, 10),
            3: get_possible_locations(3, 10),
            4: get_possible_locations(4, 10),
            5: get_possible_locations(5, 10)
        }
        self.shoot_locations: List[str] = [loc[0] for loc in get_possible_locations(1, 10)]

    def get_state(self) -> BattleshipGameState:
        return self.state

    def set_state(self, state: BattleshipGameState) -> None:
        self.state = state

    def print_state(self) -> None:
        #for idx in [0, 1]:
        for idx in [1]:
            print(f"----------- Player {idx + 1} -----------")
            if self.state.winner == idx:
                print(Back.GREEN + Fore.YELLOW + Style.BRIGHT + "Winner!" + Style.RESET_ALL)
            elif self.state.idx_player_active == idx:
                print(Fore.YELLOW + "Your turn!" + Style.RESET_ALL)
            print_player_board(
                ships=self.state.players[idx].ships,
                enemy_shots=self.state.players[(idx + 1) % 2].shots
                )
            print("--------------------------------\n")

    def get_ship_actions(self) -> List[BattleshipAction]:
        busy_locations = set()
        missing_ships = []
        for ship in self.state.get_player_ships(active_player=True):
            if ship.location is None:
                missing_ships.append(ship)
            else:
                busy_locations.update(ship.location)
        next_ship = missing_ships[0]
        actions = [
            BattleshipAction(action_type=ActionType.SET_SHIP, ship_name=next_ship.name, location=loc)
            for loc in self.ship_locations[next_ship.length]
            if len(set(loc).intersection(busy_locations)) == 0
            ]
        return actions

    def get_shoot_actions(self) -> List[BattleshipAction]:
        loc_options = set(self.shoot_locations).difference(set(self.state.get_player_shots(active_player=True)))
        return [BattleshipAction(action_type=ActionType.SHOOT, location=[loc]) for loc in loc_options]

    def get_list_action(self) -> List[BattleshipAction]:
        if not self.state.all_ships_located():
            return self.get_ship_actions()
        if self.state.phase == GamePhase.FINISHED:
            return []
        return self.get_shoot_actions()

    def apply_action(self, action: BattleshipAction) -> None:
        self.state.apply_action(action)

    def get_player_view(self, idx_player: int) -> BattleshipGameState:
        if idx_player > 1:
            raise ValueError('There are only two players')
        return self.state.get_masked_state(idx_player)


# pylint: disable = too-few-public-methods
class RandomPlayer(Player):

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> Optional[BattleshipAction]:
        """ Given masked game state and possible actions, select the next action """
        if len(actions) > 0:
            return random.choice(actions)
        return None


class NotSoRandomPlayer(Player):

    last_action = None
    last_successfull_action = None

    def get_dist(self, a: BattleshipAction, b: BattleshipAction) -> float:
        a_x = ord(a.location[0][0])
        a_y = int(a.location[0][1:])
        b_x = ord(b.location[0][0])
        b_y = int(b.location[0][1:])
        if a_x != b_x and a_y != b_y:
            return 100
        return abs(a_x - b_x) + abs(a_y - b_y)

    def select_action(self, state: BattleshipGameState, actions: List[BattleshipAction]) -> BattleshipAction:
        action_selected = None
        if state.phase == GamePhase.SETUP:
            if len(actions) > 0:
                action_selected = random.choice(actions)
        else:
            player = state.players[state.idx_player_active]
            if self.last_action is not None and self.last_action.location[0] in player.successful_shots:
                self.last_successfull_action = self.last_action
            if self.last_successfull_action is not None:
                d_min = None
                a_min = None
                for action in actions:
                    d = self.get_dist(self.last_successfull_action, action)
                    if d_min is None or d_min > d:
                        d_min = d
                        a_min = action
                action_selected = a_min
            else:
                if len(actions) > 0:
                    action_selected = random.choice(actions)

        if state.phase == GamePhase.RUNNING:
            self.last_action = action_selected
        if action_selected is None:
            raise ValueError("Can't find a suitable action")
        return action_selected


if __name__ == "__main__":

    game = Battleship()
    game.get_state()
    game.get_list_action()
    game.print_state()


    # test all ships set
    game=Battleship()
    rand_player=RandomPlayer()
    for i in range(10):
        acts = game.get_list_action()
        act = rand_player.select_action(game.get_state(), acts)
        print(act)
        if act:
            game.apply_action(act)
    print('all_ships_located:', game.state.all_ships_located())
    game.print_state()



    # test gameplay
    game=Battleship()
    smart_player=NotSoRandomPlayer()
    random.seed(4)

    CNT = 0
    while True:
        stat = game.get_state()
        if stat.idx_player_active == 0:
            CNT += 1
            if CNT >= 8:
                game.print_state()
            if CNT == 9:
                break
        if stat.phase == GamePhase.FINISHED:
            break
        act = smart_player.select_action(stat, game.get_list_action())
        game.apply_action(act)
    #game.print_state()