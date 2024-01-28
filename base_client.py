import random
from game.client.user_client import UserClient
from game.common.avatar import Avatar
from game.common.enums import *
from game.common.map.game_board import GameBoard
from game.utils.vector import Vector


class State(Enum):
    MINING = auto()
    SELLING = auto()


class Client(UserClient):
    # Variables and info you want to save between turns go here
    def __init__(self):
        super().__init__()

    def team_name(self):
        """
        Allows the team to set a team name.
        :return: Your team name
        """
        return 'OOOOOOO'
    
    def first_turn_init(self, world, avatar):
        """
        This is where you can put setup for things that should happen at the beginning of the first turn
        """
        self.company = avatar.company
        self.my_station_type = ObjectType.TURING_STATION if self.company == Company.TURING else ObjectType.CHURCH_STATION
        self.current_state = State.MINING
        self.base_position = world.get_objects(self.my_station_type)[0][0]

    # This is where your AI will decide what to do
    # def take_turn(self, turn: int, actions: [ActionType], world: GameBoard, avatar: Avatar):
    #     """
    #     This is where your AI will decide what to do.
    #     :param turn:        The current turn of the game.
    #     :param actions:     This is the actions object that you will add effort allocations or decrees to.
    #     :param world:       Generic world information
    #     """
    #     if turn == 1:
    #         self.first_turn_init(world, avatar)
            
    #     current_tile = world.game_map[avatar.position.y][avatar.position.x] # set current tile to the tile that I'm standing on
        
    #     # If I start the turn on my station, I should...
    #     if current_tile.occupied_by.object_type == self.my_station_type:
    #         # buy Improved Mining tech if I can...
    #         if avatar.science_points >= avatar.get_tech_info('Improved Drivetrain').cost and not avatar.is_researched('Improved Drivetrain'):
    #             return [ActionType.BUY_IMPROVED_DRIVETRAIN]
    #         # otherwise set my state to mining
    #         self.current_state = State.MINING
            
    #     # If I have at least 5 items in my inventory, set my state to selling
    #     if len([item for item in self.get_my_inventory(world) if item is not None]) >= 5:
    #         self.current_state = State.SELLING
            
    #     # Make action decision for this turn
    #     if self.current_state == State.SELLING:
    #         # actions = [ActionType.MOVE_LEFT if self.company == Company.TURING else ActionType.MOVE_RIGHT] # If I'm selling, move towards my base
    #         actions = self.generate_moves(avatar.position, self.base_position, turn % 2 == 0)
    #     else:
    #         if current_tile.occupied_by.object_type == ObjectType.ORE_OCCUPIABLE_STATION:
    #             # If I'm mining and I'm standing on an ore, mine it
    #             actions = [ActionType.MINE]
    #         else:
    #             # If I'm mining and I'm not standing on an ore, move randomly
    #             target = self.findNearestOre(world, avatar)
    #             if target[0] > avatar.position.y:
    #                 actions = [ActionType.MOVE_DOWN]
    #             elif target[0] < avatar.position.y:
    #                 actions = [ActionType.MOVE_UP]
    #             elif target[1] > avatar.position.x:
    #                 actions = [ActionType.MOVE_RIGHT]
    #             elif target[1] < avatar.position.x:
    #                 actions = [ActionType.MOVE_LEFT]
    #     return actions
    
    def take_turn(self, turn: int, actions: [ActionType], world: GameBoard, avatar: Avatar):
        if turn == 1:
            self.first_turn_init(world, avatar)
        if world.game_map[avatar.position.y][avatar.position.x].is_occupied_by_object_type(ObjectType.ORE_OCCUPIABLE_STATION):
            return [ActionType.MINE]
        else:
            target = self.findNearestOre(world, avatar)
            if target[1] > avatar.position.x:
                actions = [ActionType.MOVE_RIGHT,]
            elif target[1] < avatar.position.x:
                actions = [ActionType.MOVE_LEFT,]
            elif target[0] > avatar.position.y:
                actions = [ActionType.MOVE_DOWN,]
            elif target[0] < avatar.position.y:
                actions = [ActionType.MOVE_UP,]
            print("target", target)
            print(actions)
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

    def followMoves(self, tiles):
        moves = []
        currentPostion = Avatar.position

    def findNearestOre(self, world:GameBoard, avatar : Avatar):
        xToCheck = -4
        yToCheck = -4
        nearestOre=[1000, 1000]
        # print("our position", avatar.position)
        while (xToCheck < 4):
            yToCheck = -4
            while (yToCheck < 4):
                # print((((avatar.position.x + xToCheck) > 0) and ((avatar.position.y + yToCheck)>0)))
                if ((((avatar.position.x + xToCheck) >= 0) and ((avatar.position.y + yToCheck)>=0)) and (((avatar.position.x + xToCheck) <= 13) and ((avatar.position.y + yToCheck) <= 13))):
                    # print((avatar.position.y + yToCheck) , (avatar.position.x + xToCheck))
                    tileToCheck = world.game_map[avatar.position.y + yToCheck][avatar.position.x + xToCheck]
                    if (tileToCheck.is_occupied_by_object_type(ObjectType.ORE_OCCUPIABLE_STATION)):
                        newList = [(avatar.position.y + yToCheck), (avatar.position.x + xToCheck)]
                        print("new distance", self.findDistanceFromPlayer(newList, avatar), "old Distance", self.findDistanceFromPlayer(nearestOre, avatar), "location", newList)
                        if self.isWall(newList, avatar, world):
                             if (self.findDistanceFromPlayer(newList, avatar) <= self.findDistanceFromPlayer(nearestOre, avatar)):
                                nearestOre = [(avatar.position.y + yToCheck), (avatar.position.x + xToCheck)]
                yToCheck = yToCheck + 1
            xToCheck = xToCheck + 1
        return nearestOre

    def findDistanceFromPlayer(self, cord:list, avatar : Avatar):
        return abs(avatar.position.y - cord[0])+abs(avatar.position.x - cord[1])

    def isWall(self, cord: list, avatar: Avatar, world : GameBoard):
        yToIterate = avatar.position.y
        xToIterate = avatar.position.x
        while(xToIterate < cord[1]):
            xToIterate+=1
            if (world.game_map[yToIterate][xToIterate].is_occupied_by_object_type(ObjectType.WALL)):
                print("isWall = true")
                return False
        while(xToIterate > cord[1]):
            xToIterate-=1
            if (world.game_map[yToIterate][xToIterate].is_occupied_by_object_type(ObjectType.WALL)):
                print("isWall = true")
                return False
        while(yToIterate < cord[0]):
            yToIterate+=1
            if (world.game_map[yToIterate][xToIterate].is_occupied_by_object_type(ObjectType.WALL)):
                print("isWall = true")
                return False
        while(yToIterate > cord[0]):
            yToIterate-=1
            if (world.game_map[yToIterate][xToIterate].is_occupied_by_object_type(ObjectType.WALL)):
                print("isWall = true")
                return False
        print("isWall = False")
        return True