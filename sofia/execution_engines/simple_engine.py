from itertools import izip
from sofia.workflow_template import Template


class SimpleExecutionEngine(object):
    def __init__(self):
        self.resolved_entities = {}
        self.unresolved_steps = []

    def execute(self, workflow):
        self.resolved_entities = {entity: list(entity.attributes['filename']) for entity in workflow.provided_entities}
        self.unresolved_steps = list(workflow.partitions[Template.STEP_PARTITION])

        workflow.init()
        while self.output_pending(workflow):
            step = self.get_next_step()
            output = self.execute_step(step)
            self.resolved_entities.update(output)

    def resolve_entity(self, entity, value):
        self.resolved_entities[entity] = value

    def output_pending(self, workflow):
        return not all(head in self.resolved_entities for head in workflow.heads)

    def get_next_step(self):
        for step in self.unresolved_steps:
            if all(child in self.resolved_entities for child in step.ins):
                return step
        raise NotImplementedError('unexpected end in workflow execution')

    def execute_step(self, step):
        """
        Execute the named step. Also control the multiplicity of input and output entities

        :param step: step to prepare input for
        :param kwargs: input to be prepared
        :return: dict of output by entity type
        """
        keys = [in_.name for in_ in step.ins]
        input_entity_types = step.ins
        input_length, input_entities = self.get_input_entities(input_entity_types)
        output_entity_types = step.outs
        output_entities = {entity_type: [] for entity_type in output_entity_types}
        for values in izip(*input_entities):
            kwargs = dict(zip(keys, values))
            output = step.run(**kwargs)
            for entity_type, value in zip(output_entity_types, output):
                output_entities[entity_type].extend(value)
        self.unresolved_steps.remove(step)
        return output_entities

    def get_input_entities(self, entity_types):
        entities = [self.resolved_entities[entity_type] for entity_type in entity_types]
        lengths = {len(entities_) for entities_ in entities}
        if len(lengths) > 1:
            raise ValueError('unable to handle inputs of different lengths')
        return list(lengths)[0], entities
