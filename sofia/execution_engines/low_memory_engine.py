from itertools import islice


class LowMemoryExecutionEngine(object):
    def __init__(self, workflow, max_entities=10):
        self.resolved_entities = {}
        self.workflow = workflow
        self.max_entities = max_entities
        self.unresolved_steps = list(self.workflow.partitions[1])

    def execute(self):
        self.workflow.init()
        for step in self.workflow.partitions[1]:
            params = {key: step.attr[key] for key in step.PARAMS if key in step.attr}
            step.init(**params)
        while self.output_pending():
            step = self.get_next_step()
            self.execute_step(step)

    def resolve_entity(self, entity, value):
        self.resolved_entities[entity] = value

    def output_pending(self):
        return not all(head in self.resolved_entities for head in self.workflow.heads)

    def get_next_step(self):
        for step in self.unresolved_steps:
            if any(len(self.resolved_entities[child]) >= self.max_entities for child in step.outs.itervalues() if child in self.resolved_entities):
                continue
            if all(child in self.resolved_entities for child in step.ins.itervalues()):
                return step
        raise NotImplementedError('unexpected end in workflow execution')

    def execute_step(self, step):
        args = {input.name: self.resolved_entities[input] for input in step.ins.itervalues()}
        output = dict(islice(step.prepare(**args), self.max_entities))
        self.resolved_entities.update(output)
        self.unresolved_steps.remove(step)
