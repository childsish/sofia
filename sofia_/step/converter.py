__author__ = 'Liam Childs'

from step import Step


class Converter(Step):

    def register_converter(self, converter):
        self.converter = converter

    def calculate(self, **kwargs):
        entity = kwargs[self.outs.keys()[0]]
        return self.converter.convert(entity)
