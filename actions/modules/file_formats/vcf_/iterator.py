import bz2
import gzip

from collections import OrderedDict, namedtuple


Variant = namedtuple('Variant', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'samples'))
Variant.__new__.__defaults__ = (None, None, None, None, None, None, None, None, {})


class VcfLine(namedtuple('VcfLine', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'format', 'samples'))):
    def __new__(cls, chr, pos, id, ref, alt, qual, filter, info, format='', samples=''):
        return super(VcfLine, cls).__new__(cls, chr, pos, id, ref, alt, qual, filter, info, format, samples)

    def __str__(self):
        res = [self.chr, str(self.pos + 1), self.id, self.ref, self.alt, self.qual, self.filter, self.info]
        if self.format != '':
            res.append(self.format)
            res.append(self.samples)
        return '\t'.join(res)


class VcfLineIterator(object):
    def __init__(self, fname):
        self.fname = fname
        self.fhndl =\
            gzip.open(fname) if fname.endswith('.gz') else\
            bz2.BZ2File(fname) if fname.endswith('.bz2') else\
            open(fname)
        self.line_no = 0
        self.hdrs = self._parse_headers()
        self.samples = self.hdrs['##SAMPLES']
        del self.hdrs['##SAMPLES']

    def __iter__(self):
        for line in self.fhndl:
            parts = line.split('\t', 9)
            parts[1] = int(parts[1]) - 1
            yield VcfLine(*parts)

    def close(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()

    def _parse_headers(self):
        fhndl = self.fhndl
        hdrs = OrderedDict()
        line = fhndl.next().strip()
        self.line_no += 1
        if 'VCF' not in line:
            raise ValueError('Invalid VCF file. Line 1: {}'.format(line.strip()))
        while line.startswith('##'):
            key, value = line.split('=', 1)
            if key not in hdrs:
                hdrs[key] = []
            hdrs[key].append(value)
            line = fhndl.next().strip()
            self.line_no += 1
        hdrs['##SAMPLES'] = line.strip().split('\t')[9:]
        return hdrs

    def __del__(self):
        self.close()


class VcfEntryIterator(VcfLineIterator):
    
    def __init__(self, fname):
        super(VcfEntryIterator, self).__init__(fname)

    def __iter__(self):
        for line in super(VcfEntryIterator, self).__iter__():
            samples = self._parse_samples(line.format.split(':'), line.samples.split('\t'))
            yield Variant(line.chr,
                          line.pos,
                          line.id,
                          line.ref,
                          line.alt,
                          self._parse_quality(line.qual),
                          line.filter,
                          self._parse_info(line.info),
                          samples)

    @staticmethod
    def _parse_quality(qual):
        try:
            res = float(qual)
        except TypeError:
            return '.'
        return res

    @staticmethod
    def _parse_info(info):
        return dict(i.split('=', 1) if '=' in i else (i, i) for i in info.strip().split(';'))
    
    def _parse_samples(self, format, sample_data):
        res = {}
        for sample, data in zip(self.samples, sample_data):
            res[sample] = dict(zip(format, sample.split(':')))
        return res
