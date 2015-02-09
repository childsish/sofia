from sofia_.entity import Entity


class genomic_position(Entity):
    """
    A position on a chromosome.
    """

    CHILDREN = ['chromosome_id', 'position']

    def format(self, genomic_position):
        return '{}:{}'.format(genomic_position['chromosome_id'], genomic_position['position'])
