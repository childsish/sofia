from collections import defaultdict
from operator import or_
from input_stream import InputStream
from output_stream import OutputStream
from state import State


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
        try:
            step_class = step.init(self.get_input_streams(step))
        except Exception:
            raise TypeError('failed to create {}'.format(step))
        state = State(step_class,
                      self.get_output_streams(step),
                      self.indices[step])
        self.indices[step] += 1
        self.states[step].append(state)
        return state

    def can_run(self, step):
        return all(self.input_streams[step][in_].is_readable() for in_ in step.ins)

    def can_finalise(self, step):
        return all(self.input_streams[step][in_].is_finished() for in_ in step.ins)

    def get_input_streams(self, step):
        return {in_.name: self.input_streams[step][in_] for in_ in step.ins}

    def get_output_streams(self, step):
        return {out.name: OutputStream(self.threshold, self.get_consumers(step)) for out in step.outs}

    def drain_output(self, step, state):
        for out, producer_stream in zip(step.outs, state.outputs.itervalues()):
            for consumer in self.workflow.get_parents(out):
                consumer_stream = self.input_streams[consumer][out]
                consumer_stream.write(producer_stream.output, state.index)
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
