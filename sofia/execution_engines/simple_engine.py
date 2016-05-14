from collections import defaultdict

class SimpleExecutionEngine(object):
    def __init__(self, workflow):
        self.resolved_entities = {}
        self.workflow = workflow
        self.unresolved_steps = list(self.workflow.partitions[1])

    def execute(self):
        self.workflow.init()
        for step in self.workflow.partitions[1]:
            params = {key: step.attr[key] for key in step.PARAMS if key in step.attr}
            step.init(**params)
        while self.output_pending():
            step = self.get_next_step()
            output = self.execute_step(step)
            self.resolved_entities.update(output)

    def resolve_entity(self, entity, value):
        self.resolved_entities[entity] = value

    def output_pending(self):
        return not all(head in self.resolved_entities for head in self.workflow.heads)

    def get_next_step(self):
        for step in self.unresolved_steps:
            if all(child in self.resolved_entities for child in step.ins.itervalues()):
                return step
        raise NotImplementedError('unexpected end in workflow execution')

    def execute_step(self, step):
        kwargs = {input.name: self.resolved_entities[input] for input in step.ins.itervalues()}
        output = self.prepare(step, kwargs)
        self.unresolved_steps.remove(step)
        return output

    def prepare(self, step, kwargs):
        lengths = defaultdict(set)
        for key, value in kwargs.iteritems():
            lengths[len(value)].add(key)
        if len(lengths) > 2:
            raise ValueError('unable to handle inputs of different lengths')
        res = {entity: [] for entity in step.outs.itervalues()}
        for i in xrange(max(lengths)):
            args = {key: value[i % len(value)] for key, value in kwargs.iteritems()}
            values = list(step.run(**args))
            if len(step.outs) == 1:
                res[step.outs.values()[0]].extend(values)
            else:
                for entity, value in zip(step.outs.itervalues(), values):
                    res[entity].extend(value)
        return res

    def get_input(self):
