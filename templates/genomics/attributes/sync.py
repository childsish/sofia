from sofia.resolvers import AttributeResolver


class SyncResolver(AttributeResolver):

    ATTRIBUTE = 'sync'

    def resolve_out(self, ins):
        """
        Determine which stream the output is synchronised with. If the incoming streams have different sync values, then
         it is unknown what synchronisation the outgoing stream should have.  
        :param ins: dictionary of the incoming streams' sync values
        :return: 
        """
        values = set()
        for value in ins.values():
            values.update(value)
        if len(values) > 1:
            msg = 'Unable to resolve sync stream. Consider adding a custom resolver to {}.'
            raise ValueError(msg.format(self.step.name))
        return {key: values for key in self.step.outs}
