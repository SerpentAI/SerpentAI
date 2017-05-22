from .game_room import GameRoom

from lib.visual_debugger.visual_debugger import VisualDebugger

visual_debugger = VisualDebugger()


class GameFloor:
    def __init__(self, **kwargs):
        self.current_room = (0, 0)

        self.rooms = {
            (0, 0): GameRoom(is_explored=True)
        }

    def register_room(self, coordinates, minimap_cell):
        absolute_coordinates = self._get_absolute_coordinates(coordinates)

        if absolute_coordinates in self.rooms:
            return None

        self.rooms[absolute_coordinates] = GameRoom(is_explored=False, room_type=minimap_cell.room_type)

    def _get_absolute_coordinates(self, coordinates):
        return (
            self.current_room[0] + coordinates[0],
            self.current_room[1] + coordinates[1]
        )
