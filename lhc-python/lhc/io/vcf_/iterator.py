from collections import OrderedDict, namedtuple, defaultdict
from operator import or_


class Variant(namedtuple('Variant', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'samples'))):
    def __new__(cls, chr, pos, id, ref, alt, qual=None, filter=None, info=None, samples={}):
        return super(Variant, cls).__new__(cls, chr, pos, id, ref, alt, qual, filter, info, samples)

    def __str__(self):
        res = [self.chr, str(self.pos + 1), self.id, self.ref, self.alt, str(self.qual), self.filter,
               ';'.join('{}={}'.format(k, v) for k, v in self.info.iteritems())]
        format = sorted(reduce(or_, (set(sample) for sample in self.samples.itervalues())))
        if len(format) > 0:
            res.append(':'.join(format))
            for sample in self.samples.itervalues():
                res.append('.' if len(sample) == 0 else
                           ':'.join(sample[f] for f in format))
        return '\t'.join(res)


class VcfLine(namedtuple('VcfLine', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'format', 'samples'))):
    def __new__(cls, chr, pos, id, ref, alt, qual, filter, info, format=None, samples=None):
        return super(VcfLine, cls).__new__(cls, chr, pos, id, ref, alt, qual, filter, info, format, samples)

    def __str__(self):
        res = [self.chr, str(self.pos + 1), self.id, self.ref, self.alt, self.qual, self.filter, self.info]
        if self.format is not None:
            res.append(self.format)
            res.append(self.samples)
        return '\t'.join(res)


class VcfLineIterator(object):
    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.line_no = 0
        self.hdrs = self._parse_headers()
        self.samples = self.hdrs['##SAMPLES']
        del self.hdrs['##SAMPLES']

    def __iter__(self):
        return self

    def next(self):
        line = self.fileobj.next()
        self.line_no += 1
        if line == '':
            raise StopIteration()
        return self.parse_line(line)
    
    def close(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()

    def _parse_headers(self):
        fileobj = self.fileobj
        hdrs = OrderedDict()
        line = fileobj.next().strip()
        if 'VCF' not in line:
            raise ValueError('Invalid VCF file. Line 1: {}'.format(line.strip()))
        self.line_no += 1
        while line.startswith('##'):
            key, value = line.split('=', 1)
            if key not in hdrs:
                hdrs[key] = set()
            hdrs[key].add(value)
            line = fileobj.next().strip()
            self.line_no += 1
        hdrs['##SAMPLES'] = line.strip().split('\t')[9:]
        return hdrs

    def __del__(self):
        self.close()

    @staticmethod
    def parse_line(line):
        parts = line.rstrip('\r\n').split('\t', 9)
        parts[1] = int(parts[1]) - 1
        return VcfLine(*parts)


class VcfEntryIterator(VcfLineIterator):
    def __init__(self, fname):
        super(VcfEntryIterator, self).__init__(fname)

    def __iter__(self):
        return self
    
    def next(self):
        return self.parse_entry(super(VcfEntryIterator, self).next())

    def parse_entry(self, line):
        samples = None if line.samples is None else\
            self._parse_samples(line.format.split(':'), line.samples.split('\t'))
        return Variant(line.chr,
                       line.pos,
                       line.id,
                       line.ref,
                       line.alt,
                       self._parse_quality(line.qual),
                       line.filter,
                       self._parse_info(line.info),
                       samples)

    def _parse_samples(self, format, sample_data):
        res = {}
        for sample, data in zip(self.samples, sample_data):
            res[sample] = {} if data == '.' else dict(zip(format, data.split(':')))
        return res

    @staticmethod
    def _parse_quality(qual):
        try:
            res = float(qual)
        except TypeError:
            return '.'
        except ValueError:
            return '.'
        return res

    @staticmethod
    def _parse_info(info):
        return dict(i.split('=', 1) if '=' in i else (i, i) for i in info.strip().split(';'))
