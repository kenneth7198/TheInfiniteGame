"""generative_agents.maze"""

import random
from itertools import product

from modules import utils
from modules.memory.event import Event


class Tile:
    def __init__(
        self,
        coord,
        world,
        address_keys,
        address=None,
        collision=False,
    ):
        # in order: world, sector, arena, game_object
        self.coord = coord
        self.address = [world]
        if address:
            self.address += address
        self.address_keys = address_keys
        self.address_map = dict(zip(address_keys[: len(self.address)], self.address))
        self.collision = collision
        self.event_cnt = 0
        self._events = {}
        if len(self.address) == 4:
            self.add_event(Event(self.address[-1], address=self.address))

    def abstract(self):
        address = ":".join(self.address)
        if self.collision:
            address += "(collision)"
        return {
            "coord[{},{}]".format(self.coord[0], self.coord[1]): address,
            "events": {k: str(v) for k, v in self.events.items()},
        }

    def __str__(self):
        return utils.dump_dict(self.abstract())

    def __eq__(self, other):
        if isinstance(other, Tile):
            return hash(self.coord) == hash(other.coord)
        return False

    def get_events(self):
        return self.events.values()

    def add_event(self, event):
        if isinstance(event, (tuple, list)):
            event = Event.from_list(event)
        if all(e != event for e in self._events.values()):
            self._events["e_" + str(self.event_cnt)] = event
            self.event_cnt += 1
        return event

    def remove_events(self, subject=None, event=None):
        r_events = {}
        for tag, eve in self._events.items():
            if subject and eve.subject == subject:
                r_events[tag] = eve
            if event and eve == event:
                r_events[tag] = eve
        for r_eve in r_events:
            self._events.pop(r_eve)
        return r_events

    def update_events(self, event, match="subject"):
        u_events = {}
        for tag, eve in self._events.items():
            if match == "subject" and eve.subject == event.subject:
                self._events[tag] = event
                u_events[tag] = event
        return u_events

    def has_address(self, key):
        return key in self.address_map

    def get_address(self, level=None, as_list=True):
        level = level or self.address_keys[-1]
        assert level in self.address_keys, "Can not find {} from {}".format(
            level, self.address_keys
        )
        pos = self.address_keys.index(level) + 1
        if as_list:
            return self.address[:pos]
        return ":".join(self.address[:pos])

    def get_addresses(self):
        addresses = []
        if len(self.address) > 1:
            addresses = [
                ":".join(self.address[:i]) for i in range(2, len(self.address) + 1)
            ]
        return addresses

    @property
    def events(self):
        return self._events

    @property
    def is_empty(self):
        return len(self.address) == 1 and not self._events


class Maze:
    def __init__(self, config, logger):
        # define tiles
        self.maze_height, self.maze_width = config["size"]
        self.tile_size = config["tile_size"]
        address_keys = config["tile_address_keys"]
        self.tiles = [
            [
                Tile((x, y), config["world"], address_keys)
                for x in range(self.maze_width)
            ]
            for y in range(self.maze_height)
        ]
        
        for tile in config["tiles"]:
            if "coord" not in tile:
                print(f"Warning: Missing 'coord' key in tile: {tile}")
                continue  # 跳过没有 'coord' 的数据

            x, y = tile.pop("coord")
            self.tiles[y][x] = Tile((x, y), config["world"], address_keys, **tile)


        # define address
        self.address_tiles = dict()
        for i in range(self.maze_height):
            for j in range(self.maze_width):
                for add in self.tile_at([j, i]).get_addresses():
                    self.address_tiles.setdefault(add, set()).add((j, i))

        self.logger = logger

    def find_path(self, src_coord, dst_coord, retries=3):
        attempt = 0
        while attempt <= retries:
            try:
                if not (0 <= dst_coord[0] < self.maze_width and 0 <= dst_coord[1] < self.maze_height):
                    raise ValueError(f"Invalid destination coordinate: {dst_coord}. Out of bounds.")
                tile = self.tile_at(dst_coord)
                if tile.collision:
                    raise ValueError(f"Destination coordinate {dst_coord} is not reachable (collision).")

                map = [[0 if not self.tile_at((x, y)).collision else -1 for x in range(self.maze_width)] for y in range(self.maze_height)]
                frontier, visited = [src_coord], set()
                map[src_coord[1]][src_coord[0]] = 1

                while map[dst_coord[1]][dst_coord[0]] == 0:
                    new_frontier = []
                    for f in frontier:
                        for c in self.get_around(f):
                            if 0 <= c[0] < self.maze_width and 0 <= c[1] < self.maze_height and map[c[1]][c[0]] == 0:
                                map[c[1]][c[0]] = map[f[1]][f[0]] + 1
                                new_frontier.append(c)
                                visited.add(c)
                    if not new_frontier:
                        raise ValueError(f"No path found from {src_coord} to {dst_coord}")
                    frontier = new_frontier

                step = map[dst_coord[1]][dst_coord[0]]
                path = [dst_coord]
                while step > 1:
                    for c in self.get_around(path[-1]):
                        if map[c[1]][c[0]] == step - 1:
                            path.append(c)
                            break
                    step -= 1
                return path[::-1]
            except ValueError as e:
                print(f"DEBUG: Pathfinding failed for src: {src_coord}, dst: {dst_coord}. Error: {e}")
                attempt += 1
                dst_coord = self.get_random_valid_destination(src_coord)

        raise ValueError(f"Failed to find path after {retries} retries.")

    def get_random_valid_destination(self, current_coord=None):
        while True:
            if current_coord:
                random_coord = (
                    current_coord[0] + random.randint(-5, 5),
                    current_coord[1] + random.randint(-5, 5),
                )
            else:
                random_coord = (
                    random.randint(0, self.maze_width - 1),
                    random.randint(0, self.maze_height - 1),
                )
            if 0 <= random_coord[0] < self.maze_width and 0 <= random_coord[1] < self.maze_height:
                tile = self.tile_at(random_coord)
                if not tile.collision:
                    return random_coord


    def tile_at(self, coord):
        return self.tiles[coord[1]][coord[0]]

    def update_obj(self, coord, obj_event):
        tile = self.tile_at(coord)
        if not tile.has_address("game_object"):
            return
        if obj_event.address != tile.get_address("game_object"):
            return
        addr = ":".join(obj_event.address)
        if addr not in self.address_tiles:
            return
        for c in self.address_tiles[addr]:
            self.tile_at(c).update_events(obj_event)

    def get_scope(self, coord, config):
        coords = []
        vision_r = config["vision_r"]
        if config["mode"] == "box":
            x_range = [
                max(coord[0] - vision_r, 0),
                min(coord[0] + vision_r + 1, self.maze_width),
            ]
            y_range = [
                max(coord[1] - vision_r, 0),
                min(coord[1] + vision_r + 1, self.maze_height),
            ]
            coords = list(product(list(range(*x_range)), list(range(*y_range))))
        return [self.tile_at(c) for c in coords]

    def get_around(self, coord, no_collision=True):
        coords = [
            (coord[0] - 1, coord[1]),
            (coord[0] + 1, coord[1]),
            (coord[0], coord[1] - 1),
            (coord[0], coord[1] + 1),
        ]
        if no_collision:
            coords = [c for c in coords if not self.tile_at(c).collision]
        return coords

    def get_address_tiles(self, address):
        addr = ":".join(address)
        if addr in self.address_tiles:
            return self.address_tiles[addr]
        return random.choice(list(self.address_tiles.values()))
