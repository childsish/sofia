import sys

from collections import defaultdict
from itertools import repeat
from sofia.workflow_template import Template


class SimpleExecutionEngine(object):
    def __init__(self):
        self.entities = {}
        self.unresolved_steps = []

    def execute(self, workflow):
        self.entities = {entity: list(entity.attributes['filename']) for entity in workflow.provided_entities}
        self.unresolved_steps = list(workflow.partitions[Template.STEP_PARTITION])

        workflow.init()
        while self.output_pending(workflow):
            step = self.get_next_step()
            output = self.execute_step(step)
            self.entities.update(output)

        for step in workflow.partitions[Template.STEP_PARTITION]:
            warnings = step.get_user_warnings()
            if len(warnings) > 0:
                sys.stderr.write(str(step))
                sys.stderr.write('\n ')
                sys.stderr.write('\n '.join(warnings))
                sys.stderr.write('\n')

    def output_pending(self, workflow):
        return not all(head in self.entities for head in workflow.heads)

    def get_next_step(self):
        for step in self.unresolved_steps:
            if all(child in self.entities for child in step.ins):
                return step
        raise RuntimeError('only unresolved steps without inputs remaining')

    def execute_step(self, step):
        """
        Execute the named step. Also control the multiplicity of input and output entities

        :param step: step to prepare input for
        :param kwargs: input to be prepared
        :return: dict of output by entity type
        """
        inputs = self.get_inputs(step.ins)
        outputs = defaultdict(list)
        for output in step.run(inputs):
            for k, v in output.items():
                outputs[k].extend(v)
        for output in step.finalise():
            for k, v in output.items():
                outputs[k].extend(v)
        self.unresolved_steps.remove(step)
        return outputs

    def get_inputs(self, entity_types):
        entities = [self.entities[entity_type] for entity_type in entity_types]
        lengths = [len(entity) for entity in entities]
        if len(set(lengths) - {1}) > 1:
            raise ValueError('unable to handle inputs of different lengths')
        n = max(lengths)
        if n > 1:
            for i in range(len(entities)):
                if lengths[i] == 1:
                    entities[i] = repeat(entities[i][0], n)
        return zip(*entities)
