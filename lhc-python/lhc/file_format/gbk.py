#!/usr/bin/python

from lhc.binf.interval import Interval, Complement
from GenBankFileUtility import tokenise, TokeniserError
from optparse import OptionParser

class GenBankFile:
    def __init__(self, filename):
        self.gc = '0'
        self.__filename = filename
        self.hdrs = {}
        self.ftrs = {}
        self.seq = ''
        
        infile = file(filename)
        lines = infile.readlines()
        infile.close()
        
        fr = 0
        while fr < len(lines):
            to = fr + 1
            while to < len(lines) and lines[to][0] == ' ':
                to += 1
            
            if lines[fr].startswith('FEATURES'):
                self.ftrs = self.__parseFtrs(lines, fr+1, to)
            elif lines[fr].startswith('ORIGIN'):
                self.seq = self.__parseSeq(lines, fr, to)
            elif lines[fr] == '//':
                break
            else:
                hdr, val = self.__parseHdr(lines, fr, to)
                self.hdrs.setdefault(hdr, []).append(val)
            
            fr = to
        del lines
        
        self.genes = self.__parseGenes(self.ftrs)
    
    def getGeneSeq(self, gene):
        return gene['range'].get_sub_seq(self.seq)
    
    def linear_search(array, fr, x):
        _x = x
        if isinstance(x, tuple):
            _x = x[1]
        
        res = []
        while array[fr][0][0] < x[1]:
            fr += 1
        print USAGE
    
    def binary_search(array, fr, to, x):
        if to - fr <= 1:
            self.linear_search(array, fr, x)
        
        _x = x
        if isinstance(x, tuple):
            _x = x[0]
        
        m = (fr + to) / 2
        if array[m][0][0] > _x:
            return self.binary_search(array, fr, m, x)
        return self.binary_search(array, m, to, x)
    
    def featureAt(self, x):
        idx = self.binary_search(self.rngs, 0, len(self.rngs), x)
        return self.ftrs[idx]
    
    def __parseHdrs(self, lines, fr, to, lvl):
        res = {}
        prv = fr
        for i in xrange(fr+1, to):
            if lines[i][lvl] != ' ':
                hdr, val = self.__parseHdr(lines, prv, i)
                if hdr == 'REFERENCE':
                    res.setdefault(hdr, []).append(val)
                else:
                    res[hdr] = val
                prv = i
        hdr, val = self.__parseHdr(lines, prv, to)
        res[hdr] = val
        return res
    
    def __parseHdr(self, lines, fr, to):
        hdr = lines[fr][:12].strip()
        
        if hdr == 'LOCUS':
            val = lines[fr][12:].split()
        elif hdr == 'SOURCE':
            i = fr + 1
            while lines[i][:12].strip() == '':
                i += 1
            src = ' '.join([lines[j][12:].strip() for j in xrange(fr, i)])
            org = lines[i][12:].strip()
            
            fr = i + 1
            i = fr + 1
            while i < to and lines[i][:12].strip() == '':
                i += 1
            lin = ' '.join([lines[j][12:].strip() for j in xrange(fr, i)])
            
            val = {hdr: src}
            val['ORGANISM'] = org
            val['LINEAGE'] = lin
        elif hdr == 'REFERENCE':
            val = self.__parseHdrs(lines, fr+1, to, 4)
            val[hdr] = lines[fr][12:].strip()
        else:
            val = []
            for i in xrange(fr, to):
                val.append(lines[i][12:].strip())
            val = ' '.join(val)
        return hdr, val
    
    def __parseFtrs(self, lines, fr, to):
        ftrs = {}
        
        ttl = 0
        prv = fr
        for i in xrange(fr+1, to):
            if lines[i][5] != ' ':
                try:
                    typ = lines[prv][:21].strip()
                    ftr = self.__parseFtr(lines, prv, i)
                    ftr['index'] = ttl
                    ftr['gene_type'] = typ
                    ftrs.setdefault(typ, []).append(ftr)
                    ttl += 1
                except TokeniserError, e:
                    print 'Unable to tokenise feature: %s\n Ignoring...'%\
                     lines[prv].strip()
                prv = i
        typ = lines[prv][:21].strip()
        ftr = self.__parseFtr(lines, prv, to)
        ftr['index'] = ttl
        ftr['gene_type'] = typ
        ftrs.setdefault(typ, []).append(ftr)
        ttl += 1
        
        return ftrs
    
    def __parseFtr(self, lines, fr, to):
        res = {}
        
        # Parse the range
        rng_str = lines[fr][21:].strip()
        i = fr + 1
        while i < to and lines[i][21] != '/':
            rng_str += lines[i].strip()
            i += 1
        rng = self.__parseSuperRange(tokenise(rng_str))
        res['range'] = rng
        
        
        while i < to:
            j = i + 1
            while j < to and lines[j][21] != '/':
                j += 1
            key, val = self.__parseQua(lines, i, j)
            res[key] = val
            i = j
        
        #if ftr == 'rRNA':
            #print res
            #print rng_str
            #print tokenise(rng_str)
        
        return res
    
    def __parseQua(self, lines, fr, to):
        key = None
        val = None
        
        line = lines[fr].strip()
        if not '=' in lines[fr]:
            key = line[1:]
            val = True
            return key, val
        
        key = line[1:line.find('=')]
        if key == 'translation':
            val = ''.join([line.strip() for line in lines[fr:to]])
        else:
            val = ' '.join([line.strip() for line in lines[fr:to]])
        
        val = val[val.find('=')+1:]
        val = val.replace('"', '')
        
        if key == 'codon_start':
            val = int(val) - 1
        
        return key, val
    
    def __parseGenes(self, ftrs):
        res = {}
        for typ in ['CDS', 'tRNA', 'rRNA']:
            if typ not in ftrs:
                continue
            for ftr in ftrs[typ]:
                if not 'gene' in ftr:
                    # Then this is probably an unsupported gene
                    #if 'locus_tag' in ftr:
                        #ftr['gene'] = ftr['locus_tag']
                    #elif 'protein_id' in ftr:
                        #ftr['gene'] = ftr['protein_id']
                    if 'product' in ftr and 'hypothetical' not in ftr['product']:
                        ftr['gene'] = ftr['product']
                        res.setdefault(ftr['gene'], []).append(ftr)
                    #elif 'label' in ftr:
                        #ftr['gene'] = ftr['label']
                    #elif 'note' in ftr:
                        #ftr['gene'] = ftr['note']
                    #else:
                        #raise Exception('Unlabelled gene: %s'%str(ftr))
                    continue
                res.setdefault(ftr['gene'], []).append(ftr)
        return res
    
    def __parseSeq(self, lines, fr, to):
        res = []
        for i in xrange(fr, to):
            parts = lines[i].split()
            res += parts[1:]
        res = ''.join(res)
        return res
    
    def __parseSuperRange(self, tokens):
        """ Parses a super range.
         SuperRange ::= Range | Join | Complement
        """
        if tokens[0].isdigit():
            return self.__parseRange(tokens)
        elif tokens[0] in ['join', 'order']:
            return self.__parseJoin(tokens)
        elif tokens[0] == 'complement':
            return self.__parseComplement(tokens)
        else:
            raise Exception('Range %s does not fit pattern.'%str(tokens))
    
    def __parseRange(self, tokens):
        """ Parses a range
         Range ::= <num> | <num> ('..' | '^') <num>
        """
        fr = int(tokens.pop(0)) - 1
        if len(tokens) > 1 and tokens[0] in ['..', '^']:
            tokens.pop(0) # Pop '..' | '^'
            to = int(tokens.pop(0))
            return Interval(fr, to)
        
        return Interval(fr)
    
    def __parseJoin(self, tokens):
        """ Parses a join.
         Join ::= 'join' '(' SuperRange [',' SuperRange] ')'
        """
        res = []
        tokens.pop(0) # Pop 'join'
        tokens.pop(0) # Pop '('
        res.append(self.__parseSuperRange(tokens))
        while tokens[0] == ',':
            tokens.pop(0)
            res.append(self.__parseSuperRange(tokens))
        tokens.pop(0) # Pop ')'
        return Interval(res)
    
    def __parseComplement(self, tokens):
        """ Parses a complement
         Complement ::= 'complement' '(' SuperRange ')'
        """
        tokens.pop(0) # Pop 'complement'
        tokens.pop(0) # Pop '('
        res = self.__parseSuperRange(tokens)
        tokens.pop(0) # Pop ')'
        return Complement(res)

def iterGenbank(fname):
    raise 'Not yet implemented'
    infile = open(fname)
    record = False
    for line in infile:
        if line.startswith('FEATURES'):
            record = True
            continue
        elif line.startswith('ORIGIN'):
            break
        
        
    infile.close()

def split(argv):
    import os
    infname = argv[1]
    outdname = argv[2]
    
    infile = open(infname)
    outfile = None
    for line in infile:
        if line.startswith('LOCUS'):
            if outfile != None:
                outfile.close()
            outfname = '%s.gbk'%line.split()[1]
            outfile = open(os.path.join(outdname, outfname), 'w')
        outfile.write(line)
    outfile.close()
    infile.close()

def extract(argv):
    # Warning, if rng.f is less than 0, the retrieved sequence will be wrong...
    parser = OptionParser(usage='usage: %prog extract [options] infile')
    parser.set_defaults(ext5=0, ext3=0, paths=[], types=[])
    parser.add_option('-5', '--5p', action='store', type='int', dest='ext5',
     help='Extend the sequence in the  5\'direction.')
    parser.add_option('-3', '--3p', action='store', type='int', dest='ext3',
     help='Extend the sequence in the  3\'direction.')
    parser.add_option('-p', '--path', action='append', type='string', nargs=3,
     dest='paths',
     help='Extract a sequence using the given paths (eg. CDS gene nptII)')
    parser.add_option('-t', '--type', action='append', type='string', nargs=1,
     dest='types', help='Extract a feature type (eg. CDS)')
    parser.add_option('-w', '--wrap', action='store', type='int', nargs=1,
     dest='wrap', help='Wrap the sequence')
    options, args = parser.parse_args(argv[1:])
    
    fname = args[0]
    genes = args[1:]
    gbk = GenBankFile(fname)
    if len(options.paths) == 0 and len(options.types) == 0:
        sys.stdout.write('>whole_sequence\n')
        if options.wrap:
            for i in xrange(0, len(gbk.seq), options.wrap):
                sys.stdout.write(gbk.seq[i:i+options.wrap])
                sys.stdout.write('\n')
                
        else:
            sys.stdout.write(gbk.seq)
            sys.stdout.write('\n')
    
    extractGenes(genes, gbk, options)
    if len(options.paths) > 0:
        extractPaths(gbk, options)
    if len(options.types) > 0:
        extractType(gbk, options)

def extractGenes(genes, gbk, options):
    for gene in genes:
        ftr = None
        for typ, ftrs in gbk.ftrs.iteritems():
            for f in ftrs:
                if 'label' in f and f['label'] == gene:
                    ftr = f
                    break
            if ftr != None:
                break
        if ftr == None:
            sys.stdout.write('Unable to find %s\n'%gene)
            continue
        
        hdr = [gene]
        if options.ext5 != 0:
            hdr.append('atg:%d'%(options.ext5))
        if options.ext3 != 0:
            hdr.append('end:%d'%(options.ext3))
        rng5p = ftr['range'].get5pInterval(-options.ext5)
        rng3p = ftr['range'].get3pInterval(options.ext3)
        rng = rng5p | ftr['range'] | rng3p
        print rng5p
        print ftr['range']
        print rng3p
        seq = rng.get_sub_seq(gbk.seq)
        
        sys.stdout.write('>%s\n%s\n'%(' '.join(hdr), seq))

def extractPaths(gbk, options):
    for typ, qua, val in options.paths:
        cnt = 0
        for ftr in gbk.ftrs[typ]:
            if ftr[qua] == val:
                rng5p = ftr['range'].get5pInterval(-options.ext5)
                rng3p = ftr['range'].get3pInterval(options.ext3)
                rng = rng5p | ftr['range'] | rng3p
                print rng5p
                print ftr['range']
                print rng3p
                print rng
                seq = rng.get_sub_seq(gbk.seq)
                hdr = ['%s_%s_%s.%s'%(typ, qua, val, cnt)]
                if options.ext5 != 0:
                    hdr.append('atg:%d'%(options.ext5))
                if options.ext3 != 0:
                    hdr.append('end:%d'%(options.ext3))
                sys.stdout.write('>%s\n%s\n'%(' '.join(hdr), seq))
                cnt += 1
        if cnt == 0:
            sys.stdout.write('Path %s %s %s does not exist\n'%(typ, qua, val))

def extractType(gbk, options):
    for typ in options.types:
        cnt = 0
        for ftr in gbk.ftrs[typ]:
            rng = ftr['range']
            rng.adj5p(-options.ext5)
            rng.adj3p(options.ext3)
            seq = rng.get_sub_seq(gbk.seq)
            hdr = ['%s.%d'%(typ, cnt)]
            if options.ext5 != 0:
                hdr.append('atg:%d'%(options.ext5))
            if options.ext3 != 0:
                hdr.append('end:%d'%(options.ext3))
            sys.stdout.write('>%s\n%s\n'%(' '.join(hdr), seq))
            cnt += 1
        if cnt == 0:
            sys.stdout.write('Path %s does not exist\n'%(typ))

USAGE = 'python GenBankFile.py [options]\n' +\
 'Options:\n' +\
 'split    split a multiple GenBank file into parts\n' +\
 'extract  extract a particular sequence from the GenBank file\n'

def main(argv):
    if len(argv) <= 1:
        print USAGE
    if argv[1] == 'split':
        split(argv[1:])
    elif argv[1] == 'extract':
        extract(argv[1:])
    elif argv[1] == 'help':
        help()
    else:
        print USAGE
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
