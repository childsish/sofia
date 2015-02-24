from action import Action


class Map(Action):
    def init(self, in_cols, out_cols, filename):
        fhndl = open(filename)
        fhndl.readline()
        lines = (line.rstrip('\r\n').split('\t') for line in fhndl)
        self.map = {tuple(parts[col] for col in in_cols): parts[out_cols[0]] for parts in lines}\
            if len(out_cols) == 1 else\
            {tuple(parts[col] for col in in_cols): tuple(parts[col] for col in out_cols) for parts in lines}
        fhndl.close()

    def calculate(self, **kwargs):
        key = tuple(kwargs[in_] for in_ in self.ins)
        return self.map[key]
