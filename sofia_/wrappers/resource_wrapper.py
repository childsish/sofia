from step_wrapper import StepWrapper


class ResourceWrapper(StepWrapper):
    def __init__(self, step_class, name=None, ins=None, outs=None, attr={}, format=None, ext=None):
        super(ResourceWrapper, self).__init__(step_class, name, ins, outs, attr)
        self.format = step_class.FORMAT if format is None else format
        self.ext = step_class.EXT if ext is None else ext

    def matches(self, resource):
        """ Check if a disk-based source matches this resource. """
        if resource.name is not None:
            return resource.name == self.format
        return any(resource.attr['filename'].endswith(ext) for ext in self.ext)
