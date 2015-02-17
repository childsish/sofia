class ColumnTracker(object):
    def __init__(self, columns, type):
        self.current_key = None
        self.columns = columns
        self.type = type

    def convert(self, parts):
        return self.type(*[parts[column] for column in self.columns])

    def get_key(self):
        return self.current_key

    def is_new_entry(self, parts):
        raise NotImplementedError()

    def set_new_entry(self, parts):
        self.current_key = self.convert(parts)


class KeyColumnTracker(ColumnTracker):
    def is_new_entry(self, parts):
        key = self.convert(parts)
        if self.current_key is None:
            self.current_key = key
            return False
        elif self.current_key != key:
            return True
        return False


class IntervalColumnTracker(ColumnTracker):
    def get_key(self):
        return self.current_key.start

    def is_new_entry(self, parts):
        interval = self.convert(parts)
        if self.current_key is None:
            self.current_key = interval
            return False
        elif self.current_key.stop <= interval.start:
            return True
        self.current_key.stop = max(self.current_key.stop, interval.stop)
        return False
