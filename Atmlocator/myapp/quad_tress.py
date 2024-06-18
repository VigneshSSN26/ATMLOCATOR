class Location:
    def __init__(self, name, latitude, longitude, full_address):
        self.name = name
        self.x = latitude
        self.y = longitude
        self.full_address = full_address

    def __repr__(self):
        return f"Location({self.name}, {self.x}, {self.y}, {self.full_address})"

class QNode:
    def __init__(self, location, nw=None, ne=None, sw=None, se=None):
        self.location = location
        self.nw = nw
        self.ne = ne
        self.sw = sw
        self.se = se

class QuadTree:
    def __init__(self, root_location):
        self.root = QNode(root_location)

    def insert(self, location):
        self._insert(self.root, location)

    def _insert(self, node, location):
        if location.x < node.location.x:  # west
            if location.y < node.location.y:  # south
                if node.sw is None:
                    node.sw = QNode(location)
                else:
                    self._insert(node.sw, location)
            else:  # north
                if node.nw is None:
                    node.nw = QNode(location)
                else:
                    self._insert(node.nw, location)
        else:  # east
            if location.y < node.location.y:  # south
                if node.se is None:
                    node.se = QNode(location)
                else:
                    self._insert(node.se, location)
            else:  # north
                if node.ne is None:
                    node.ne = QNode(location)
                else:
                    self._insert(node.ne, location)

    def search_closest_node(self, node, location):
        closest_node = node
        closest_distance = self._distance(node.location, location)

        directions = [(node.nw, "nw"), (node.ne, "ne"), (node.sw, "sw"), (node.se, "se")]

        for next_node, _ in directions:
            if next_node:
                dist = self._distance(next_node.location, location)
                if dist < closest_distance:
                    closest_node = next_node
                    closest_distance = dist

        if closest_node != node:
            return self.search_closest_node(closest_node, location)
        else:
            return closest_node, closest_distance

    @staticmethod
    def _distance(loc1, loc2):
        return ((loc1.x - loc2.x) ** 2 + (loc1.y - loc2.y) ** 2) ** 0.5
