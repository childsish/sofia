import sys

from buffer import Buffer
from multiprocessing import Process, Pipe
from operator import or_
from sofia.execution_engines.workers import parallel_worker, step_worker
from sofia.workflow_template import Template


class ParallelExecutionEngine(object):
    def __init__(self, max_entities=100, max_cpus=4):
        self.max_entities = max_entities
        self.max_cpus = max_cpus

    def execute(self, workflow):
        workflow.init()
        steps = workflow.partitions[Template.STEP_PARTITION]
        inputs = {step: Buffer(step.ins, self.max_entities) for step in steps}

        to_step = {}
        from_step = {}
        step_processes = {}
        for step in steps:
            parent_conn, child_conn = Pipe()
            to_step[step] = parent_conn
            from_step[step] = child_conn
            process = Process(target=step_worker, args=(step, child_conn, self.max_entities))
            process.start()
            step_processes[step] = process

        to_worker, from_worker = Pipe()
        processes = []
        for i in xrange(self.max_cpus):
            process = Process(target=parallel_worker, args=(from_worker, to_step))
            process.start()
            processes.append(process)

        exhausted = {}
        for entity in workflow.provided_entities:
            if entity not in workflow.graph:
                continue
            for consumer in workflow.get_parents(entity):
                exhausted[consumer] = {entity}
                inputs[consumer].write(entity, entity.attributes['filename'])
                if inputs[consumer].is_readable():
                    to_worker.send(('run', {'step': consumer, 'input': inputs[consumer].read()}))

        status = {}
        stopped = 0
        while stopped < self.max_cpus:
            message, data = to_worker.recv()
            sys.stderr.write('master recieved "{}" from {}\n'.format(message, data['step']))

            if message == 'running':
                status[data['step']] = 'running'
                for producer in self.get_producers(data['step'], workflow):
                    if self.can_next(producer, inputs, workflow, status):
                        sys.stderr.write('master sending "next" to {}\n'.format(producer))
                        to_worker.send(('next', {'step': producer}))
                    elif status[producer] == 'stopped':
                        exhausted[data['step']] |= (producer.outs & data['step'].ins)
            elif message == 'finalising':
                status[data['step']] = 'finalising'
            elif message == 'data':
                consumers = reduce(or_, (workflow.get_parents(out) for out in data['data']))
                for consumer in consumers:
                    for entity in set(consumer.ins) & set(data['data'].iterkeys()):
                        inputs[consumer].write(entity, data['data'][entity])
                    if self.can_run(consumer, inputs):
                        sys.stderr.write('master sending "run" to {}\n'.format(consumer))
                        to_worker.send(('run', {'step': consumer, 'input': inputs[consumer].read()}))
            elif message == 'stop':
                if status[data['step']] == 'running' and self.can_finalise(data['step'], exhausted, status):
                    sys.stderr.write('master sending "finalise" to {}\n'.format(data['step']))
                    to_worker.send(('finalise', data['step']))
                elif status[data['step']] == 'finalising':
                    pass
                status[data['step']] = 'stopped'
            elif message == 'stopped':
                stopped += 1
            else:
                raise ValueError('unknown message: {}'.format(message))

        for process in processes:
            process.join()
        for connection in to_step.itervalues():
            connection.send('stop')
        for step_process in step_processes:
            step_process.join()

    def get_producers(self, step, workflow):
        return reduce(or_, (workflow.get_parents(in_) for in_ in step.ins))

    def get_consumers(self, step, workflow):
        return reduce(or_, (workflow.get_children(out) for out in step.outs))

    def can_run(self, step, inputs):
        """
        All the inputs are filled
        :param step:
        :param inputs:
        :param workflow:
        :return:
        """
        return inputs[step].is_readable()

    def can_finalise(self, step, exhausted, status):
        """
        The step is running and the inputs are exhausted
        :param step:
        :param exhausted:
        :return:
        """
        return status[step] == 'running' and all(in_ in exhausted[step] for in_ in step.ins)

    def can_next(self, step, inputs, workflow, status):
        """
        All the outputs are empty and status is running or finalising
        :param step:
        :param inputs:
        :param workflow:
        :param status:
        :return:
        """
        if step in status and status[step] not in {'running', 'finalising'}:
            return False
        for out in step.outs:
            if not all(inputs[consumer].is_writable(out) for consumer in workflow.get_parents(out)):
                return False
        return True
