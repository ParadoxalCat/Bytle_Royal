import random

from game.client.user_client import UserClient
from game.common.avatar import Avatar
from game.common.enums import *
from game.common.map.game_board import GameBoard
from game.utils.vector import Vector


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
            avatar.position.x]  # set current tuple to the tuple that I'm standing on

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

        self.current_state = State.TEST
        # Make action decision for this turn
        if self.current_state == State.SELLING:
            # actions = [ActionType.MOVE_LEFT if self.company == Company.TURING else ActionType.MOVE_RIGHT] # If I'm selling, move towards my base
            actions = self.generate_moves(avatar.position, self.base_position, turn % 2 == 0)
        elif State.TEST:
            tuples = self.astar(world, avatar.position, Vector(2, 3))
            actions = self.moveVector(avatar.position, tuples[1])
        else:
            if current_tile.occupied_by.object_type == ObjectType.ORE_OCCUPIABLE_STATION:
                # If I'm mining and I'm standing on an ore, mine it
                actions = [ActionType.MINE]
            else:
                # If I'm mining and I'm not standing on an ore, move randomly
                actions = [random.choice(
                    [ActionType.MOVE_LEFT, ActionType.MOVE_RIGHT, ActionType.MOVE_UP, ActionType.MOVE_DOWN])]

        return actions

    def generate_moves(self, start_position, end_position, vertical_first):
        """
        This function will generate a path between the start and end position. It does not consider walls and will
        try to walk directly to the end position.
        :param start_position:      Position to start at
        :param end_position:        Position to get to
        :param vertical_first:      True if the path should be vertical first, False if the path should be horizontal first
        :return:                    Path represented as a list of ActionType
        """
        dx = end_position.x - start_position.x
        dy = end_position.y - start_position.y

        horizontal = [ActionType.MOVE_LEFT] * -dx if dx < 0 else [ActionType.MOVE_RIGHT] * dx
        vertical = [ActionType.MOVE_UP] * -dy if dy < 0 else [ActionType.MOVE_DOWN] * dy

        return vertical + horizontal if vertical_first else horizontal + vertical

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
    def generate_tuples_around(self, tuple, world):
        tuples = []
        tuple_up = (tuple[0], tuple[1] - 1)
        tuple_down = (tuple[0], tuple[1] + 1)
        tuple_right = (tuple[0] + 1, tuple[1])
        tuple_left = (tuple[0] - 1, tuple[1])

        if not world.game_map[tuple_up[0]][tuple_up[1]].is_occupied_by_object_type(ObjectType.WALL):
            tuples.append(tuple_up)
        if not world.game_map[tuple_down[0]][tuple_down[1]].is_occupied_by_object_type(ObjectType.WALL):
            tuples.append(tuple_down)
        if not world.game_map[tuple_right[0]][tuple_right[1]].is_occupied_by_object_type(ObjectType.WALL):
            tuples.append(tuple_right)
        if not world.game_map[tuple_left[0]][tuple_left[1]].is_occupied_by_object_type(ObjectType.WALL):
            tuples.append(tuple_left)

        return tuples
    def generate_vectors_around(self, vector, world):
        tiles = []

        tile_up = world.game_map[vector.y - 1][vector.x]
        tile_down = world.game_map[vector.y + 1][vector.x]
        tile_right = world.game_map[vector.y][vector.x + 1]
        tile_left = world.game_map[vector.y][vector.x - 1]

        if not tile_up.is_occupied_by_object_type(ObjectType.WALL):
            tile_up = Vector(vector.y - 1, vector.x)
            if 13 >= tile_up.x >= 0 or 13 >= tile_up.y >= 0:
                tiles.append((0, tile_up.y))
        if not tile_down.is_occupied_by_object_type(ObjectType.WALL):
            tile_down = Vector(vector.y + 1, vector.x)
            if 13 >= tile_down.x >= 0 or 13 >= tile_down.y >= 0:
                tiles.append((0, tile_down.y))
        if not tile_right.is_occupied_by_object_type(ObjectType.WALL):
            tile_right = Vector(vector.y, vector.x + 1)
            if 13 >= tile_right.x >= 0 or 13 >= tile_right.y >= 0:
                tiles.append((tile_right.x, 0))
        if not tile_left.is_occupied_by_object_type(ObjectType.WALL):
            tile_left = Vector(vector.y, vector.x - 1)
            if 13 >= tile_left.x >= 0 or 13 >= tile_left.y >= 0:
                tiles.append((tile_left.x, 0))
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

    class Node():
        """A node class for A* Pathfinding"""

        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position = position

            self.g = 0
            self.h = 0
            self.f = 0

        def __eq__(self, other):
            return self.position == other.position

    def astar(self, maze, start, end):
        """Returns a list of tuples as a path from the given start to the given end in the given maze"""

        start_node = self.Node(None, start)
        start_node.g = start_node.h = start_node.f = 0
        end_node = self.Node(None, end)
        end_node.g = end_node.h = end_node.f = 0

        open_list = []
        closed_list = []

        open_list.append(start_node)

        while len(open_list) > 0:

            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)

            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            children = []
            for new_position in [Vector(0, -1), Vector(0, 1), Vector(-1, 0), Vector(1, 0)]:  # Adjacent squares

                node_position = Vector(current_node.position.x + new_position.x, current_node.position.y + new_position.y)

                if node_position.x > 13 or node_position.x < 0 or node_position.y > 13 or node_position.y < 0:
                    continue

                if maze.game_map[node_position.y][node_position.x].is_occupied_by(ObjectType.WALL):
                    continue

                new_node = self.Node(current_node, node_position)

                children.append(new_node)

            for child in children:

                for closed_child in closed_list:
                    if child == closed_child:
                        continue
                child.g = current_node.g + 1
                child.h = abs(child.position.x - end_node.position.x) + abs(
                    child.position.y - end_node.position.y)
                child.f = child.g + child.h

                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                open_list.append(child)


