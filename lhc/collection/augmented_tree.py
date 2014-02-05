#!/usr/bin/python
# Not complete...

class AugmentedTree:
    """ Built to hold several Range objects. """
    
    class Node:
        def __init__(self, points, f, t):
            self.p = None
            self.l = None
            self.r = None
            
            if f == t:
                return
            
            m = (f + t)/2
            
            self.p = points[m]
            self.l = AugmentedTree.Node(points, f, m)
            self.r = AugmentedTree.Node(points, m+1, t)
        
        def __str__(self):
            if self.p == None:
                return str(self.p)
            return str(self.p) + '\nl' + str(self.l) + '\nr' + str(self.r)
        
        def insert(self, p):
            if self.p == None:
                self.p = p
                self.l = AugmentedTree.Node(None, 0, 0)
                self.r = AugmentedTree.Node(None, 0, 0)
                return
            
            if self.p.f <= p.f:
                self.l.insert(p)
            else:
                self.r.insert(point)
        
        def query(self, rng):
            res = []
            if rng.overlaps(self.p):
                res.append(self.p)
            
            if self.r.p != None:
                res += self.l.query(rng)
                if self.r.p.f < rng.t:
                    res += self.r.query(rng)
            
            return res
    
    def __init__(self, points):
        points.sort(key=lambda x:x.f)
        self.head = AugmentedTree.Node(points, 0, len(points))
    
    def __str__(self):
        return str(self.head)
    
    def insert(self, point):
        self.head.insert(point)
    
    def query(self, rng):
        self.head.query(rng)

def main(argv = None):
    import random
    import Range
    import itertools
    
    if argv == None:
        argv = sys.argv
    
    points = [Range.Range(random.randint(0, 100), random.randint(0, 100))
              for i in itertools.repeat(None, 10)]
    print points
    
    tree = AugmentedTree(points)
    
    print tree

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
