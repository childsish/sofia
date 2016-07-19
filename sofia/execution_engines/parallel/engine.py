import sys
from multiprocessing import Process, Pipe

from sofia.execution_engines.state_manager import StateManager
from sofia.workflow_template import Template
from worker import worker


class ParallelExecutionEngine(object):
    def __init__(self, max_entities=100, max_cpus=4):
        self.max_entities = max_entities
        self.max_cpus = max_cpus

    def execute(self, workflow):
        steps = workflow.partitions[Template.STEP_PARTITION]
        state_manager = StateManager(steps, workflow, self.max_entities)
        processes, conn = self.start_processes(workflow, state_manager)

        try:
            self.loop(steps, conn, state_manager)
            for process in processes:
                conn.send(('stop', None, None))
                process.join()
        except Exception:
            for process in processes:
                process.terminate()
            raise

    def loop(self, steps, conn, state_manager):
        finalised = set()
        while not finalised.issuperset(steps):
            message, step, state = conn.recv()
            sys.stderr.write('master recieved "{}" for {}\n'.format(message, step))

            if message == 'running':
                state_manager.drain_output(step, state)
                for consumer in state_manager.get_consumers(step):
                    if state_manager.can_run(consumer):
                        state_ = state_manager.get_state(consumer)
                        conn.send(('run', consumer, state_))
                conn.send(('run', step, state))
            elif message == 'stopped':
                state_manager.drain_output(step, state)
                for consumer in state_manager.get_consumers(step):
                    if state_manager.can_run(consumer):
                        state_ = state_manager.get_state(consumer)
                        conn.send(('run', consumer, state_))
                producers = state_manager.get_producers(step)
                if len(producers) == 0 or state_manager.can_finalise(step):
                    conn.send(('finalise', step, state))
            elif message == 'finalising':
                state_manager.drain_output(step, state)
                for consumer in state_manager.get_consumers(step):
                    if state_manager.can_run(consumer):
                        state_ = state_manager.get_state(consumer)
                        conn.send(('run', consumer, state_))
                conn.send(('finalise', step, state))
            elif message == 'finalised':
                finalised.add(step)
                state_manager.drain_output(step, state)
                state_manager.finish_output(step)
                for consumer in state_manager.get_consumers(step):
                    if state_manager.can_run(consumer):
                        state_ = state_manager.get_state(consumer)
                        conn.send(('run', consumer, state_))
                    elif state_manager.can_finalise(consumer):
                        state_ = state_manager.get_state(consumer)
                        conn.send(('finalise', consumer, state_))
            else:
                raise ValueError('recieved unknown message from worker: {}'.format(message))

    def start_processes(self, workflow, state_manager):
        to_worker, from_worker = Pipe()
        processes = []
        for i in xrange(self.max_cpus):
            process = Process(target=worker, args=(i, from_worker))
            process.start()
            processes.append(process)

        for entity in workflow.provided_entities:
            if entity not in workflow.graph:
                continue
            for consumer in workflow.get_parents(entity):
                state_manager.input_streams[consumer][entity].write(entity.attributes['filename'], 0)
                if state_manager.can_run(consumer):
                    state = state_manager.get_state(consumer)
                    to_worker.send(('run', consumer, state))

        return processes, to_worker
