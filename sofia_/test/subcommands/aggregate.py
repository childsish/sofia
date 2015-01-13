import unittest

from sofia_.subcommands import aggregate


class TestAggregate(unittest.TestCase):
    def test_parse_resources(self):
        ress = aggregate.parseResources(['/tmp/tmp.vcf:tmp:in=asdf,fdsa:out=lkjh,hjkl', '/tmp/tmp.vcf:in=asdf'])
        print ress

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
