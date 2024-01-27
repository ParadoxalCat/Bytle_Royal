from typing import Self

from game.common.avatar import Avatar
from game.common.enums import ObjectType
from game.common.game_object import GameObject
from game.common.items.item import Item
from game.common.map.occupiable import Occupiable
from game.common.stations.station import Station


# create station object that contains occupied_by
class OccupiableStation(Occupiable, Station):
    """
    `OccupiableStation Class Notes:`

        Occupiable Station objects inherit from both the Occupiable and Station classes. This allows for other objects to
        be "on top" of the Occupiable Station. For example, an Avatar object can be on top of this object. Since Stations
        can contain items, items can be stored in this object too.

        Any GameObject or Item can be in an Occupiable Station.

        Occupiable Station Example is a small file that shows an example of how this class can be
        used. The example class can be deleted or expanded upon if necessary.
    """

    def __init__(self, held_item: Item | None = None, occupied_by: GameObject | None = None):
        super().__init__(occupied_by=occupied_by, held_item=held_item)
        self.object_type: ObjectType = ObjectType.OCCUPIABLE_STATION
        self.held_item = held_item
        self.occupied_by = occupied_by