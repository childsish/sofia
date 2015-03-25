class Partitioner(object):
    def __init__(self, fname, column_trackers, comment_chars={'#'}):
        self.fhndl = open(fname)
        self.column_trackers = column_trackers
        self.comment_chars = comment_chars
        self.buffer = self.fhndl.next()
        while any(self.buffer.startswith(char) for char in self.comment_chars):
            self.buffer = self.fhndl.next()
        parts = self.buffer.rstrip('\r\n').split('\t')
        for tracker in column_trackers:
            tracker.set_new_entry(parts)
        self.break_block = False

    def __iter__(self):
        return self

    def next(self):
        if self.buffer is None:
            raise StopIteration
        for line in self.fhndl:
            parts = line.rstrip('\r\n').split('\t')
            is_new_entry = [tracker.is_new_entry(parts) for tracker in self.column_trackers]
            if any(is_new_entry):
                buffer = self.buffer
                key = tuple(tracker.get_key() for tracker in self.column_trackers)
                break_block = self.break_block

                self.buffer = line
                for tracker in self.column_trackers:
                    tracker.set_new_entry(parts)
                self.break_block = any(is_new_entry[:-1])

                return buffer, key, break_block
            self.buffer += line
        buffer = self.buffer
        self.buffer = None
        return buffer, tuple(tracker.get_key() for tracker in self.column_trackers), self.break_block
