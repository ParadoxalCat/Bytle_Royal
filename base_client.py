import random

from game.client.user_client import UserClient
from game.common.enums import *


class State(Enum):
    MINING = auto()
    SELLING = auto()
    TEST = auto()


class Client(UserClient):
    # Variables and info you want to save between turns go here
    def __init__(self):
        super().__init__()

    def team_name(self):
        """
        Allows the team to set a team name.
        :return: Your team name
        """
        return 'The Real Jean'

    def first_turn_init(self, world, avatar):
        """
        This is where you can put setup for things that should happen at the beginning of the first turn
        """
        self.company = avatar.company
        self.my_station_type = ObjectType.TURING_STATION if self.company == Company.TURING else ObjectType.CHURCH_STATION
        self.current_state = State.MINING
        self.base_position = world.get_objects(self.my_station_type)[0][0]

    # This is where your AI will decide what to do
    def take_turn(self, turn, actions, world, avatar):
        """
        This is where your AI will decide what to do.
        :param turn:        The current turn of the game.
        :param actions:     This is the actions object that you will add effort allocations or decrees to.
        :param world:       Generic world information
        """
        if turn == 1:
            self.first_turn_init(world, avatar)

        current_tile = world.game_map[avatar.position.y][
            avatar.position.x]  # set current tile to the tile that I'm standing on

        # If I start the turn on my station, I should...
        if current_tile.occupied_by.object_type == self.my_station_type:
            # buy Improved Mining tech if I can...
            if avatar.science_points >= avatar.get_tech_info('Improved Drivetrain').cost and not avatar.is_researched(
                    'Improved Drivetrain'):
                return [ActionType.BUY_IMPROVED_DRIVETRAIN]
            # otherwise set my state to mining
            self.current_state = State.MINING

        # If I have at least 5 items in my inventory, set my state to selling
        if len([item for item in self.get_my_inventory(world) if item is not None]) >= 5:
            self.current_state = State.SELLING

        # Make action decision for this turn
        if self.current_state == State.SELLING:
            # actions = [ActionType.MOVE_LEFT if self.company == Company.TURING else ActionType.MOVE_RIGHT] # If I'm selling, move towards my base
            actions = self.generate_moves(avatar.position, self.base_position)
        else:
            if current_tile.occupied_by.object_type == ObjectType.ORE_OCCUPIABLE_STATION:
                # If I'm mining and I'm standing on an ore, mine it
                actions = [ActionType.MINE]
            else:
                # If I'm mining and I'm not standing on an ore, move randomly
                actions = [random.choice(
                    [ActionType.MOVE_LEFT, ActionType.MOVE_RIGHT, ActionType.MOVE_UP, ActionType.MOVE_DOWN])]

        return actions

    def generate_moves(self, start_position, tiles):
        """
        This function will generate a path between the start and end position. It does not consider walls and will
        try to walk directly to the end position.
        :param start_position:      Position to start at
        :param end_position:        Position to get to
        :param vertical_first:      True if the path should be vertical first, False if the path should be horizontal first
        :return:                    Path represented as a list of ActionType
        """

        moves = []
        for tile in tiles:

            dx = tile.x - start_position.x
            dy = tile.y - start_position.y

            horizontal = [ActionType.MOVE_LEFT] * -dx if dx < 0 else [ActionType.MOVE_RIGHT] * dx
            vertical = [ActionType.MOVE_UP] * -dy if dy < 0 else [ActionType.MOVE_DOWN] * dy
            moves.append(vertical + horizontal)

        return moves
    
    def get_my_inventory(self, world):
        return world.inventory_manager.get_inventory(self.company)

    def get_my_inventory(self, world):
        return world.inventory_manager.get_inventory(self.company)

    def generate_moves_around(self, tile, world):
        moves = []
        tile_up = world.game_map[tile.y - 1][tile.x]
        tile_down = world.game_map[tile.y + 1][tile.x]
        tile_right = world.game_map[tile.y][tile.x + 1]
        tile_left = world.game_map[tile.y][tile.x - 1]

        if not tile_up.is_occupied_by_object_type(ObjectType.WALL):
            moves.append(ActionType.MOVE_UP)
        if not tile_down.is_occupied_by_object_type(ObjectType.WALL):
            moves.append(ActionType.MOVE_DOWN)
        if not tile_right.is_occupied_by_object_type(ObjectType.WALL):
            moves.append(ActionType.MOVE_RIGHT)
        if not tile_left.is_occupied_by_object_type(ObjectType.WALL):
            moves.append(ActionType.MOVE_DOWN)

        return moves

    def generate_tiles_around(self, tile, world):
        tiles = []
        tile_up = world.game_map[tile.y - 1][tile.x]
        tile_down = world.game_map[tile.y + 1][tile.x]
        tile_right = world.game_map[tile.y][tile.x + 1]
        tile_left = world.game_map[tile.y][tile.x - 1]

        if not tile_up.is_occupied_by_object_type(ObjectType.WALL):
            tiles.append(tile_up)
        if not tile_down.is_occupied_by_object_type(ObjectType.WALL):
            tiles.append(tile_down)
        if not tile_right.is_occupied_by_object_type(ObjectType.WALL):
            tiles.append(tile_right)
        if not tile_left.is_occupied_by_object_type(ObjectType.WALL):
            tiles.append(tile_left)

        return tiles

    def generate_tiles_to_target(self, world, current_tile, target, path=[]):
        path.append(current_tile)
        if current_tile.occupied_by(target):
            return path
        shortest = None

        tiles_to_search = self.generate_tiles_around(current_tile, world)

        for tile in tiles_to_search:
            if tile in path:
                continue
            x = self.generate_tiles_to_target(tile, target, path)
            if shortest is None or len(x) < len(shortest):
                shortest = x

        return shortest

