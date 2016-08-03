from multiprocessing.reduction import reduce_pipe_connection, rebuild_pipe_connection


class SharedFile(object):
    def __init__(self, filename, connection):
        self.filename = filename
        self.connection = connection

    def readlines(self):
        self.connection.send((self.filename, 'readlines', []))
        return self.connection.recv()

    def __getstate__(self):
        return self.filename, reduce_pipe_connection(self.connection)

    def __setstate__(self, state):
        self.filename, self.connection = state
        self.connection = rebuild_pipe_connection(self.connection)
