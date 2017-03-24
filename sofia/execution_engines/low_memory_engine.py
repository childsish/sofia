import sys

from sofia.workflow_template import Template
from sofia.execution_engines.buffer import Buffer


class LowMemoryExecutionEngine(object):
    def __init__(self, max_entities=100):
        self.max_entities = max_entities

    def execute(self, workflow):
        workflow.init()
        steps = workflow.partitions[Template.STEP_PARTITION]
        inputs = {step: Buffer(step.ins, self.max_entities) for step in steps}
        status = {step: 'active' for step in steps}
        exhausted = set()

        stack = []
        for entity in workflow.provided_entities:
            if entity not in workflow.graph:
                continue
            for consumer in workflow.get_children(entity):
                inputs[consumer].write(entity, entity.attributes['filename'])
                if inputs[consumer].is_readable():
                    stack.append((consumer, consumer.run(inputs[consumer].read(), self.max_entities)))
            exhausted.add(entity)

        while len(stack) > 0:
            step, state = stack.pop(0)
            #sys.stderr.write('{}, {}\n'.format(step, len(stack)))
            if not self.can_run(step, inputs, workflow):
                stack.append((step, state))
                continue
            try:
                entities = next(state)
                for entity, values in entities.items():
                    for consumer in workflow.get_children(entity):
                        inputs[consumer].write(entity, values)
                        if inputs[consumer].is_readable():
                            stack.append((consumer, consumer.run(inputs[consumer].read(), self.max_entities)))
                stack.append((step, state))
            except StopIteration:
                if status[step] == 'active' and all(in_ in exhausted for in_ in step.ins):
                    stack.append((step, step.finalise(self.max_entities)))
                    status[step] = 'finalising'
                elif status[step] == 'finalising':
                    for out in step.outs:
                        exhausted.add(out)
                    status[step] = 'finalised'

    def can_run(self, step, inputs, workflow):
        for out in step.outs:
            if not all(inputs[consumer].is_writable(out) for consumer in workflow.get_children(out)):
                return False
        return True
