from collections import defaultdict
from functools import reduce
from operator import or_
from .input_stream import InputStream
from .output_stream import OutputStream
from .state import State
from .stream_set import StreamSet


class StateManager(object):
    def __init__(self, steps, workflow, threshold):
        self.input_streams = {}
        self.states = defaultdict(list)

        self.steps = steps
        self.workflow = workflow
        self.threshold = threshold

        self.indices = {}
        for step in steps:
            self.indices[step] = 0
            self.input_streams[step] = {}
            for in_ in step.ins:
                self.input_streams[step][in_] = InputStream(threshold)

    def get_state(self, step):
        syncs = reduce(or_, (in_.attributes.get('sync', set()) for in_ in step.ins))
        synced = len(syncs) == 1
        if not synced and step in self.states:
            return self.states[step][0]

        input_streams = self.get_input_streams(step)
        if synced:
            n = min(len(stream) for stream in input_streams)
            input_streams = [stream.consume(n) for stream in input_streams]

        try:
            step_class = step.init()
        except Exception as e:
            import sys
            sys.stderr.write(e.message + '\n')
            raise TypeError('failed to create {}'.format(step))

        state = State(step_class,
                      StreamSet([in_.name for in_ in step.ins], input_streams),
                      StreamSet([out.name for out in step.outs], self.get_output_streams(step)),
                      self.indices[step])
        self.indices[step] += 1
        self.states[step].append(state)
        return state

    def can_run(self, step):
        return all(in_.is_readable() for in_ in self.get_input_streams(step))

    def is_done(self, step):
        return all(in_ for in_ in self.get_input_streams(step))

    def get_input_streams(self, step):
        return [self.input_streams[step][in_] for in_ in step.ins]

    def get_output_streams(self, step):
        return [OutputStream(self.threshold, self.get_consumers(step)) for out in step.outs]

    def drain_output(self, step, state):
        for out, producer_stream in zip(step.outs, state.outputs.values()):
            for consumer in self.workflow.get_parents(out):
                consumer_stream = self.input_streams[consumer][out]
                consumer_stream.write(producer_stream.output, state.index, state.is_done)
            producer_stream.consume()

    def finish_output(self, step):
        for out in step.outs:
            for consumer in self.workflow.get_parents(out):
                consumer_stream = self.input_streams[consumer][out]
                consumer_stream.finished = True

    def get_producers(self, step):
        return reduce(or_, (self.workflow.get_children(in_) for in_ in step.ins))

    def get_consumers(self, step):
        return reduce(or_, (self.workflow.get_parents(out) for out in step.outs))
