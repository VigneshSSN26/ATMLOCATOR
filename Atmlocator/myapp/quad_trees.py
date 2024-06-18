#quad trees
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self,o):
        return ((self.x - o.x)**2 + (self.y - o.y)**2)**0.5
    
    def __str__(self):
        return f'({self.x},{self.y})' 

class QNode():
    def __init__(self,key, parent=None):
        self.key = key
        self.parent = parent
        self.ne = None
        self.se = None
        self.sw = None
        self.nw = None
        
    def __str__(self) -> str:
        return f'{self.key}'
    
    def __repr__(self) -> str:
        return str(self)
    
    def check_leaf(self):
        return (self.ne == self.nw == self.se == self.sw == None)

class QuadTree():
    
    def __init__(self, root):
        if isinstance(root, QNode):
            self.root = root
        else:
            self.root = QNode(root)
            
    def _check_quadrant(self, node, arg):
        if arg.x > node.key.x:
            if arg.y > node.key.y:
                if node.ne:
                    return node.ne
            else:
                if node.se:
                    return node.se
        else:
            if arg.y > node.key.y:
                if node.nw:
                    return node.nw
            else:
                if node.sw:
                    return node.sw
            
    def insert(self, arg):
        if not isinstance(arg, Point):
            raise 'Only point class values accepted'
        node = self.root
        
        if node==None:
            return QuadTree(arg)
        else:
            while True:
                assert node.key!=arg, 'point already exists'
                nextNode = self._check_quadrant(node, arg)
                if nextNode is None:
                    break
                else:
                    node = nextNode
            
            arg = QNode(arg)
            if arg.key.x > node.key.x:
                    if arg.key.y > node.key.y:
                        node.ne = arg
                    else:
                        node.se = arg
            else:
                if arg.key.y > node.key.y:
                    node.nw = arg
                else:
                    node.sw = arg
            arg.parent = node
            return arg
        
    def _find_quadrant(self, node, arg):
        if arg.x > node.key.x:
            if arg.y > node.key.y:
                return 'ne'
            else:
                return 'se'
        else:
            if arg.y > node.key.y:
                return 'nw'
            else:
                return 'sw'
            
    def _find_closest_border_nodes(self, node, arg):
        quadrant = self._find_quadrant(node, arg)
        abs_y = abs(arg.y-node.key.y)
        abs_x = abs(arg.x-node.key.x)
        if (abs_y > abs_x):
            if quadrant[0]=='n':
                if quadrant[1]=='e':
                    return (node.nw,)
                return (node.ne,)
            else:
                if quadrant[1]=='e':
                    return (node.sw,)
                return (node.se,)
        elif (abs_y < abs_x):
            if quadrant[0]=='n':
                if quadrant[1]=='e':
                    return (node.se,)
                else:
                    return (node.sw,)
            else:
                if quadrant[1]=='e':
                    return (node.ne,)
                else:
                    return (node.nw,)
        else:
            if quadrant=='ne' or quadrant=='sw':
                return (node.se, node.nw)
            elif quadrant=='nw' or quadrant=='se':
                return (node.ne, node.sw)
            
        
    def search_closest_node(self, node, target):
        ''' returns closest node provided the points are inserted in sorted order of x-coordinates
        '''
        if not isinstance(target, Point):
            return ValueError
        else:
            def closest_so_far(node, closest_tuple):
                if node==None:
                    return closest_tuple
                else:
                    d1 = target.distance(node.key)
                    if d1<=closest_tuple[1]:
                        closest_tuple = (node, d1)
                        
                    quadrant_node = self._check_quadrant(node, target)
                    if quadrant_node:
                        d2 = target.distance(quadrant_node.key)
                        if d2<closest_tuple[1]:
                            closest_tuple = closest_so_far(quadrant_node, closest_tuple)
                            
                    for new_node in self._find_closest_border_nodes(node, target):
                        try:
                            temp = target.distance(new_node.key)
                            if temp<=closest_tuple[1]:
                                closest_tuple = closest_so_far(new_node, closest_tuple)
                        except AttributeError:
                            pass
                return closest_tuple
            
            return closest_so_far(node, (None, float('inf')))


if __name__=='__main__':
    q = QuadTree(Point(1,1))
    q.insert(Point(1,4))
    q.insert(Point(3,3))
    q.insert(Point(4,2))
    q.insert(Point(5,4))
    print(q.search_closest_node(q.root, Point(5,3)))
                    