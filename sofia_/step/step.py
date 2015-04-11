from sofia_.entity import Entity
from sofia_.error_manager import ERROR_MANAGER
from operator import or_


class Step(object):
    """ A step that can be calculated from resources and other steps. """
    
    IN = []
    OUT = []
    
    def __init__(self, resources=None, dependencies=None, param={}, ins=None, outs=None, converters={}, name=None):
        # TODO: Consider equivalence of dependencies and ins
        self.changed = True
        self.calculated = False
        self.resources = set() if resources is None else resources
        self.dependencies = {} if dependencies is None else dependencies
        self.param = param
        #self.ins = {in_: in_ for in_ in self.IN} if ins is None else ins
        self.ins = ins
        self.outs = {out: Entity(out) for out in self.OUT} if outs is None else outs
        self.name = self._get_name(name)
        self.converters = converters
    
    def __str__(self):
        """ Return the name of the step based on it's resources and
        arguments. """
        return self.name
    
    def init(self):
        """ Initialise the step.

        When overridden, this function can be passed arguments that are parsed
        from the command line.
        """
        pass
    
    def calculate(self, **kwargs):
        """Calculate this step
        
        Assumes dependencies are already resolved. This function must be
        overridden when implementing new steps.
        
        :param dict entities: currently calculated entities. The target is at
            entities['target'].
        """
        raise NotImplementedError('You must override this function')

    def format(self, entity):
        """Convert entity produced by this step to a string
        
        :param object entity: convert this entity
        """
        return str(entity)
    
    def generate(self, entities, steps, entity_graph):
        """Generate a step
        
        This function resolves all dependencies and then calculates the
        step.
        
        :param dict entities: currently calculated entities
        :param steps: available steps
        :type steps: dict of steps
        """
        # TODO: implement proper multiple output support
        outs = self.outs
        if self.calculated:
            return  # entities[name]
        
        dependencies_changed = False
        for step in self.dependencies.itervalues():
            steps[step].generate(entities, steps, entity_graph)
            if steps[step].changed:
                dependencies_changed = True
        if not dependencies_changed and all(out in entities for out in outs):
            self.calculated = True
            self.changed = False
            return
        
        local_entities = {}
        for entity, step in self.dependencies.iteritems():
            for out in steps[step].outs:
                if entity_graph.is_equivalent(entity, out):
                    local_entities[entity] = entities[out]
        for entity, converter in self.converters.iteritems():
            local_entities[entity] = None if local_entities[entity] is None else converter.convert(local_entities[entity])

        res = [self.calculate(**local_entities)] if len(outs) == 1 else\
            self.calculate(**local_entities)
        self.calculated = True
        self.changed = False
        for out, entity in zip(outs, res):
            if out not in entities or entities[out] is not entity:
                self.changed = True
            entities[out] = entity
    
    def reset(self, steps):
        """ Resets the calculation status of this step and all dependencies
        to False.
        """
        self.calculated = False
        for step in self.dependencies.itervalues():
            steps[step].reset(steps)
    
    def get_attributes(self):
        res = {}
        for out in self.outs.itervalues():
            res.update(out.attr)
        return res
    
    def _get_name(self, name=None):
        """ Return the name of the step based on it's resources and
        arguments. """
        name = [type(self).__name__ if name is None else name]
        if len(self.resources) != 0:
            tmp = ','.join(resource.name for resource in self.resources if resource.name != 'target')
            if len(tmp) > 0:
                name.append('-r ' + tmp)
        if len(self.param) != 0:
            tmp = ','.join('{0}={0}'.format(e) for e in self.param.iteritems())
            name.append('-p ' + tmp)
        if len(self.outs) != 0:
            tmp = []
            for entity in self.outs.itervalues():
                tmp.extend((k, v) for k, v in entity.attr.iteritems() if v is not None)
            tmp = ','.join('{0}={0}'.format(e) for e in tmp)
            if len(tmp) > 0:
                name.append('-a ' + tmp)
        return '\\n'.join(name)
    
    @classmethod
    def get_output(cls, ins={}, outs={}, requested_attr={}, entity_graph=None):
        """ Determine the attributes of the outputs

        Given the provided and requested attributes, determine the output
        attributes.
        """
        #TODO use the entity graph to return proper entities with attributes
        # Check that input entity attributes match
        common_attr_names = set.intersection(*[set(entity.attr) for entity in ins.itervalues()])
        for name in common_attr_names:
            common_attr = {entity.attr[name] for entity in ins.itervalues()}
            if len(common_attr) > 1:
                attributes = ', '.join('({}: {})'.format(k, v.attr[name]) for k, v in ins.iteritems())
                ERROR_MANAGER.add_error('{} could not match {} attributes: {}'.format(cls.__name__, name, attributes))
                return None

        # Determine attributes to remove
        # FIXME: Make this per output entity rather than for all.
        in_descendents = set(ins)
        in_equivalents = reduce(or_, (entity_graph.get_equivalent_ancestors(entity) for entity in ins))
        for entity in in_equivalents:
            paths = entity_graph.get_descendent_paths(entity)
            for path in paths:
                for step in path:
                    in_descendents.update(entity_graph.get_equivalent_ancestors(step['name']))
        out_descendents = set(outs)
        out_equivalents = reduce(or_, (entity_graph.get_equivalent_ancestors(entity) for entity in outs))
        for entity in out_equivalents:
            paths = entity_graph.get_descendent_paths(entity)
            for path in paths:
                for step in path:
                    out_descendents.update(entity_graph.get_equivalent_ancestors(step['name']))
        
        # Yield the output entities
        out_attr = {}
        for entity in ins.itervalues():
            out_attr.update(entity.attr)
        remove = set()
        for attr in out_attr:
            if attr in in_descendents and attr not in out_descendents:
                remove.add(attr)
        for attr in remove:
            del out_attr[attr]
        outs = {out: Entity(out, out_attr) for out in outs}
        return outs
        #return {out: ENTITY_FACTORY.makeEntity(out, attr) for out in outs}
