import sys

from operator import or_
from sofia.workflow_template import Template
from buffer import Buffer


class LowMemoryExecutionEngine(object):
    def __init__(self, max_entities=100):
        if max_entities == 1:
            raise ValueError('Well done. You did it. You broke the algorithm. Congratulations, I hope you are happy now.')
        self.max_entities = max_entities

    def execute(self, workflow):
        steps = workflow.partitions[Template.STEP_PARTITION]
        inputs = {step: Buffer(step.ins, self.max_entities) for step in steps}
        status = {step: 'active' for step in steps}
        exhausted = set()

        for entity in workflow.provided_entities:
            if entity not in workflow.graph:
                continue
            exhausted.add(entity)
            for consumer in workflow.get_parents(entity):
                inputs[consumer].write(entity, entity.attributes['filename'])

        workflow.init()
        stack = []
        for step in steps:
            if inputs[step].is_readable():
                stack.append((step, step.run(zip(*inputs[step].read()), self.max_entities)))
        while len(stack) > 0:
            step, state = stack.pop(0)
            if self.is_frozen(step, inputs, workflow):
                status[step] = 'finalised'
                continue
            elif not self.can_run(step, inputs, workflow):
                stack.append((step, state))
                continue
            try:
                entities = state.next()
                for entity, values in entities.iteritems():
                    for consumer in workflow.get_parents(entity):
                        inputs[consumer].write(entity, values)
                        if inputs[consumer].is_readable():
                            stack.append((consumer, consumer.run(zip(*inputs[consumer].read()), self.max_entities)))
                stack.append((step, state))
            except StopIteration:
                if status[step] == 'active' and all(in_ in exhausted for in_ in step.ins):
                    stack.append((step, step.finalise()))
                    status[step] = 'finalising'
                elif status[step] == 'finalising':
                    for out in step.outs:
                        exhausted.add(out)
                    status[step] = 'finalised'
                    self.finalise_siblings(step, inputs, workflow, status)

    def is_frozen(self, step, inputs, workflow):
        consumers = reduce(or_, (workflow.get_parents(entity) for entity in workflow.get_parents(step))) - {step}
        for consumer in consumers:
            if any(out in inputs[consumer].frozen for out in step.outs):
                return True
        return False

    def can_run(self, step, inputs, workflow):
        for out in step.outs:
            for consumer in workflow.get_parents(out):
                if not inputs[consumer].is_writable([out]):
                    return False
        return True

    def finalise_siblings(self, step, inputs, workflow, status):
        siblings = reduce(or_, (workflow.get_children(entity) for entity in workflow.get_parents(step))) - {step}
        for sibling in siblings:
            outs = workflow.get_parents(sibling)
            if all(entity in inputs[sibling].frozen for entity in workflow.get_parents(sibling)):
                status[sibling] = 'finalised'
