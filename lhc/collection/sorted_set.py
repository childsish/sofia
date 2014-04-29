from bisect import bisect_left

class SortedSet(object):
    def __init__(self, iterable=[]):
        self.container = list()
        for item in iterable:
            self.add(item)

    def __str__(self):
        return 'SortedSet(%s)'%self.container
    
    def __iter__(self):
        return iter(self.container)

    def __len__(self):
        return len(self.container)

    def __contains__(self, item):
        idx = bisect_left(self.container, item)
        return idx < len(self.container) and self.container[idx] == item

    def __getitem__(self, idx):
        return self.container[idx]
    
    def __delitem__(self, idx):
        del self.container[idx]

    def add(self, item):
        idx = bisect_left(self.container, item)
        if idx >= len(self.container) or self.container[idx] != item:
            self.container.insert(idx, item)

    def pop(self):
        return self.container.pop()
