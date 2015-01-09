from lxml import etree

def iterOrpha(fname):
    tree = etree.parse(fname)
    
    for disorder in tree.find('DisorderList').iter('Disorder'):
        yield disorder.findtext('OrphaNumber'), disorder
