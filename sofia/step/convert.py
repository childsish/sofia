from step import Step


class Convert(Step):
    def __str__(self):
        return str(self.converter)

    def register_converter(self, converter):
        self.converter = converter

    def run(self, **kwargs):
        entity = kwargs[self.outs.keys()[0]]
        return None if entity is None else self.converter.convert(entity)

    def get_user_warnings(self):
        frq = round(self.converter.cnt / float(self.converter.ttl), 3)
        return {'{}% of identifiers were converted.'.format(frq * 100)} if frq < 1 else {}
