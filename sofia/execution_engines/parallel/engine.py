import sys
from multiprocessing import Process, Pipe

from sofia.execution_engines.state_manager import StateManager
from sofia.step import EndOfStream
from sofia.workflow_template import Template
from worker import worker


class ParallelExecutionEngine(object):
    def __init__(self, max_entities=100, max_cpus=4):
        self.max_entities = max_entities
        self.max_cpus = max_cpus

    def execute(self, workflow):
        steps = workflow.partitions[Template.STEP_PARTITION]
        state_manager = StateManager(steps, workflow, self.max_entities)
        processes, conn = self.start_processes()

        try:
            self.initialise_streams(workflow, state_manager, conn)
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
            step, state = conn.recv()
            sys.stderr.write('master recieved data for {}\n'.format(step))

            if state.has_ended():
                finalised.add(step)
            state_manager.drain_output(step, state)
            for consumer in state_manager.get_consumers(step):
                if state_manager.can_run(consumer):
                    conn.send(('run', consumer, state_manager.get_state(consumer)))
            if state.can_run():
                conn.send(('run', step, state))

    def start_processes(self):
        to_worker, from_worker = Pipe()
        processes = []
        for i in xrange(self.max_cpus):
            process = Process(target=worker, args=(i, from_worker))
            process.start()
            processes.append(process)
        return processes, to_worker

    def initialise_streams(self, workflow, state_manager, conn):
        for entity in workflow.provided_entities:
            if entity not in workflow.graph:
                continue
            for consumer in workflow.get_parents(entity):
                state_manager.input_streams[consumer][entity].write(list(entity.attributes['filename']), 0)
                state_manager.input_streams[consumer][entity].write([EndOfStream], 0)
                if state_manager.can_run(consumer):
                    state = state_manager.get_state(consumer)
                    conn.send(('run', consumer, state))
