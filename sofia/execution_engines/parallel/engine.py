import sys
from multiprocessing import Process, Pipe

from lhc.filetools import SharedConnection, file_worker
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
        file_process, file_worker_connection = self.get_file_worker()
        state_manager = StateManager(steps, workflow, self.max_entities)
        processes, conn = self.start_processes()

        try:
            self.initialise_streams(workflow, state_manager, conn, file_worker_connection)
            self.loop(steps, conn, state_manager)
            file_worker_connection.send(('stop', None))
            file_process.join()
            for process in processes:
                conn.send(('stop', None, None))
                process.join()
        except Exception:
            file_process.terminate()
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

    def get_file_worker(self):
        to_worker, from_worker = Pipe()
        file_process = Process(target=file_worker, args=(from_worker,))
        file_process.start()
        return file_process, SharedConnection(to_worker)

    def start_processes(self):
        processes = []
        to_worker, from_worker = Pipe()
        for i in xrange(self.max_cpus):
            process = Process(target=worker, args=(i, from_worker))
            process.start()
            processes.append(process)
        return processes, to_worker

    def initialise_streams(self, workflow, state_manager, conn, file_worker_connection):
        for entity_type in workflow.provided_entities:
            if entity_type not in workflow.graph:
                continue
            entity = [file_worker_connection] if entity_type.name == 'file_worker' else\
                list(entity_type.attributes['filename']) if entity_type.name.endswith('_file') else\
                None
            if entity is None:
                raise ValueError('unknown entity type: {}'.format(entity_type))

            for consumer in workflow.get_parents(entity_type):
                state_manager.input_streams[consumer][entity_type].write(entity, 0)
                state_manager.input_streams[consumer][entity_type].write([EndOfStream], 0)
                if state_manager.can_run(consumer):
                    state = state_manager.get_state(consumer)
                    conn.send(('run', consumer, state))
