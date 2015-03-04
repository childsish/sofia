from sofia_.entity import Entity
from sofia_.error_manager import ERROR_MANAGER


class Action(object):
    """ A action that can be calculated from resources and other steps. """
    
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
        """ Return the name of the action based on it's resources and
        arguments. """
        return self.name
    
    def init(self):
        """ Initialise the action.

        When overridden, this function can be passed arguments that are parsed
        from the command line.
        """
        pass
    
    def calculate(self, **kwargs):
        """Calculate this action
        
        Assumes dependencies are already resolved. This function must be
        overridden when implementing new steps.
        
        :param dict entities: currently calculated entities. The target is at
            entities['target'].
        """
        raise NotImplementedError('You must override this function')

    def format(self, entity):
        """Convert entity produced by this action to a string
        
        :param object entity: convert this entity
        """
        return str(entity)
    
    def generate(self, entities, actions):
        """Generate a action
        
        This function resolves all dependencies and then calculates the
        action.
        
        :param dict entities: currently calculated entities
        :param actions: available steps
        :type actions: dict of actions
        """
        # TODO: implement proper multiple output support
        name = self.name
        if self.calculated:
            return  # entities[name]
        
        dependencies_changed = False
        for action in self.dependencies.itervalues():
            actions[action].generate(entities, actions)
            if actions[action].changed:
                dependencies_changed = True
        if not dependencies_changed and name in entities:
            self.calculated = True
            self.changed = False
            return  # entities[name]
        
        local_entities = {}
        for dependency_name, action in self.dependencies.iteritems():
            outs = actions[action].outs.keys()
            if len(outs) == 1:
                local_entities[dependency_name] = entities[action]
            else:
                local_entities[dependency_name] = dict(zip(outs, entities[action]))[dependency_name]
        for edge, converter in self.converters.iteritems():
            converter.convert(local_entities)

        res = self.calculate(**local_entities)
        self.calculated = True
        self.changed = not (name in entities and entities[name] is res)
        entities[name] = res
        return  # res
    
    def reset(self, actions):
        """ Resets the calculation status of this action and all dependencies 
        to False.
        """
        self.calculated = False
        for action in self.dependencies.itervalues():
            actions[action].reset(actions)
    
    def get_attributes(self):
        res = {}
        for out in self.outs.itervalues():
            res.update(out.attr)
        return res
    
    def _get_name(self, name=None):
        """ Return the name of the action based on it's resources and
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
    def get_output(cls, ins={}, outs={}, requested_attr={}):
        """ Determine the attributes of the outputs

        Given the provided and requested attributes, determine the output
        attributes.
        """
        #TODO use the entity graph to return proper entities with attributes
        # Check that input entity attributes match
        common_attr_names = set.intersection(*[set(entity.attr) for entity in ins.itervalues()])
        for name in common_attr_names:
            common_attr = set()
            for entity in ins.itervalues():
                common_attr.add(entity.attr[name])
            if len(common_attr) > 1:
                attributes = ', '.join('({}: {})'.format(k, v.attr[name]) for k, v in ins.iteritems())
                ERROR_MANAGER.add_error('{} could not match {} attributes: {}'.format(cls.__name__, name, attributes))
                return None
        
        # Yield the output entities
        out_attr = {}
        for entity in ins.itervalues():
            out_attr.update(entity.attr)
        outs = {out: Entity(out, out_attr) for out in outs}
        return outs
        #return {out: ENTITY_FACTORY.makeEntity(out, attr) for out in outs}
