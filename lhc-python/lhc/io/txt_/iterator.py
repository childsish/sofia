from entry_guesser import EntryGuesser


class Iterator(object):
    def __init__(self, fname, entry_factory=None, comment='#', skip=0, delimiter='\t'):
        """
        Default assumes tab-delimited fields with no header and comments lines starting with "#"
        :param fname: the csv file to iterate over
        :param entry_factory: an function that builds the entry from the line parts (after splitting)
        :param comment: the character used to denote the beginning of a comment
        :param skip: the number of lines to skip. Usually 0 or 1 (ie. no header or header)
        :param delimiter: the character used to split the line
        :return:
        """
        self.line_no = 0
        self.skipped = 0

        self.fhndl = open(fname)
        self.entry_factory = EntryGuesser().guess_entry(fname) if entry_factory is None else entry_factory
        self.delimiter = delimiter
        self.skip = skip
        self.comment = comment

    def __del__(self):
        if hasattr(self, 'fhndl'):
            self.fhndl.close()

    def __iter__(self):
        return self

    def next(self):
        while True:
            line = self.fhndl.next()
            self.line_no += 1
            if not line.startswith(self.delimiter):
                if self.skipped >= self.skip:
                    break
                self.skipped += 1

        parts = line.rstrip('\r\n').split(self.delimiter)
        return self.entry_factory(parts)
