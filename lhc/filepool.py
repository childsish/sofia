import errno
import time

class FilePool(object):
    """A pool of files
    
    FilePool should be used if you think you might be opening more files than
    allowed by the operating system (2048 on many systems). If too many files
    are opened, this pool will close the one that was used the longest time
    ago.
    """
    def __init__(self, mode='r'):
        self.mode = mode
        self.last_access = {}
        self.files = {}
    
    def __contains__(self, key):
        return key in self.files
    
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
    
    def close(self, key=None):
        if key is None:
            for file in self.files.itervalues():
                file.close()
        else:
            self.files[key].close()
