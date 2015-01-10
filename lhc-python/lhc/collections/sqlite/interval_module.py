class IntervalModule(object):
    
    MINBIN = 3
    MAXBIN = 7
    
    def __init__(self, conn):
        self.conn = conn
        self.ivls = None
    
    def getQuery(self, ivl):
        qry1 = '''SELECT id, start, stop
            FROM interval
            WHERE bin == {bin} AND
                start < :stop AND
                :start < stop'''
        qry2 = '''SELECT id, start, stop
            FROM interval
            WHERE bin BETWEEN {lower} AND {upper} AND
                start < :stop AND
                :start < stop'''
        
        qry = []
        bins = self._getOverlappingBins(ivl)
        for bin in bins:
            if bin[0] == bin[1]:
                qry.append(qry1.format(bin=bin[0]))
            else:
                qry.append(qry2.format(lower=bin[0], upper=bin[1]))
        return '\nUNION\n'.join(qry)
    
    def insertInterval(self, ivl):
        cur = self.conn.cursor()
        if self.ivls is None:
            self.ivls = self._loadIntervals()
        key = (ivl.start, ivl.stop)
        if key not in self.ivls:
            qry = 'INSERT INTO interval VALUES (NULL, :start, :stop, :bin)'
            bin = self._getBin(ivl)
            cur.execute(qry, {'start': ivl.start, 'stop': ivl.stop, 'bin': bin})
            self.ivls[key] = cur.lastrowid
        return self.ivls[key]
    
    def createTable(self):
        cur = self.conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS interval (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start INTEGER,
            stop INTEGER,
            bin INTEGER
        )''')
    
    def createIndex(self):
        cur = self.conn.cursor()
        cur.execute('CREATE INDEX interval_lookup ON interval(bin, start, stop)')
        
    def _loadIntervals(self):
        cur = self.conn.cursor()
        qry = 'SELECT id, start, stop FROM interval'
        return {(start, stop): id for id, start, stop in cur.execute(qry)}
        
    def _getBin(self, ivl):
        for i in range(IntervalModule.MINBIN, IntervalModule.MAXBIN + 1):
            binLevel = 10 ** i
            if int(ivl.start / binLevel) == int(ivl.stop / binLevel):
                return int(i * 10 ** (IntervalModule.MAXBIN + 1) + int(ivl.start / binLevel))
        return int((IntervalModule.MAXBIN + 1) * 10 ** (IntervalModule.MAXBIN + 1))
    
    def _getOverlappingBins(self, ivl):
        res = []
        bigBin = int((IntervalModule.MAXBIN + 1) * 10 ** (IntervalModule.MAXBIN + 1))
        for i in range(IntervalModule.MINBIN, IntervalModule.MAXBIN + 1):
            binLevel = 10 ** i
            res.append((int(i * 10 ** (IntervalModule.MAXBIN + 1) + int(ivl.start / binLevel)),
                        int(i * 10 ** (IntervalModule.MAXBIN + 1) + int(ivl.stop / binLevel))))
        res.append((bigBin, bigBin))
        return res
