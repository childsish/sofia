import errno
import time

class FilePool(object):
    def __init__(self, mode='r'):
        self.mode = mode
        self.last_access = {}
        self.files = {}
    
    def __getitem__(self, key):
        if key not in self.files or self.files[key].closed:
            attempt = 0
            opened = False
            while attempt < 5:
                try:
                    mode = 'r' if self.mode == 'r' else 'a' if key in self.last_access else 'w'
                    self.files[key] = open(key, mode)
                    opened = True
                except IOError, e:
                    if e.errno == errno.EMFILE:
                        oldest = sorted(self.last_access.iteritems(), key=lambda x:x[1])[0][0]
                        self.files[oldest].close()
                    else:
                        raise e
                attempt += 1
            if not opened:
                raise IOError('Unable to open another file')
        self.last_access[key] = time.time()
        return self.files[key]
