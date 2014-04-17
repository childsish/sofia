from bisect import insort_left, bisect_left

class sortedset(object):
    def __init__(self, iterable=[]):
        self.container = list()
        for item in iterable:
            self.add(item)

    def __str__(self):
        return 'sortedset(%s)'%self.container

    def __len__(self):
        return len(self.container)

    def __contains__(self, item):
        if len(self.container) == 0:
            return False
        idx = bisect_left(self.container, item)
        if len(self.container) == idx:
            return False
        return self.container[idx] == item

    def __getitem__(self, key):
        return self.container[key]
    
    def __delitem__(self, key):
        del self.container[key]
    
    def __iter__(self):
        return iter(self.container)

    def add(self, item):
        if item not in self:
            insort_left(self.container, item)

    def pop(self):
        return self.container.pop()
