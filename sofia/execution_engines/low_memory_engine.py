import sys

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
        outputs = {step: Buffer(step.outs, self.max_entities) for step in steps}
        states = {step: None for step in steps}

        for entity in workflow.provided_entities:
            for consumer in workflow.get_parents(entity):
                inputs[consumer].write(entity, entity.attributes['filename'])

        workflow.init()
        while any(inputs[step].is_readable() or states[step] is not None for step in steps):
            self.tick(workflow, inputs, outputs, states)
            self.tock(workflow, inputs, outputs)

    def tick(self, workflow, inputs, outputs, states):
        """
        Resolve all necessary actions for the steps
        :param workflow: resolved workflow
        :param inputs: input buffers
        :param outputs: output buffers
        :param states: step states
        :return:
        """
        for step in workflow.partitions[Template.STEP_PARTITION]:
            if not outputs[step].is_writable(step.outs):
                continue
            elif states[step] is not None:
                try:
                    entities = states[step].next()
                    for key, values in entities.iteritems():
                        outputs[step].write(key, values)
                    sys.stderr.write(' {} output {}\n'.format(step, ', '.join(e.name for e in entities)))
                except StopIteration:
                    states[step] = None
                    if step.not_finalised:
                        states[step] = step.finalise()
            elif inputs[step].is_readable():
                sys.stderr.write('{} consumed {}\n'.format(step, ', '.join(e.name for e in step.ins)))
                states[step] = step.run(zip(*inputs[step].read()), self.max_entities)

    def tock(self, workflow, inputs, outputs):
        """
        Resolve all necessary actions for the entities
        :param workflow: resolved workflow
        :param inputs: input buffers
        :param outputs: output buffers
        :return:
        """
        for entity in workflow.partitions[Template.ENTITY_PARTITION]:
            producers = workflow.get_children(entity)
            if len(producers) == 0:
                continue
            assert len(producers) == 1
            buffer = outputs[list(producers)[0]]
            if not buffer.is_readable():
                continue
            consumers = workflow.get_parents(entity)
            if any(not inputs[consumer].is_writable([entity]) for consumer in consumers):
                continue
            for consumer in consumers:
                inputs[consumer].write(entity, buffer.items[entity])
            buffer.items[entity] = []
