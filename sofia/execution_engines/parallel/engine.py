import sys
from multiprocessing import Process, Pipe

from lhc.filetools import SharedFilePool
from sofia.execution_engines.state_manager import StateManager
from sofia.step import EndOfStream
from sofia.workflow_template import Template
from .worker import worker


class WorkerError(Exception):
    def __init__(self, value, tb):
        super(WorkerError, self).__init__(value)
        self.tb = tb


class ParallelExecutionEngine(object):
    def __init__(self, max_entities=100, max_cpus=4):
        self.max_entities = max_entities
        self.max_cpus = max_cpus

    def execute(self, workflow):
        steps = workflow.partitions[Template.STEP_PARTITION]
        filepool = SharedFilePool()
        state_manager = StateManager(steps, workflow, self.max_entities)
        processes, conn = self.start_processes()

        try:
            self.initialise_streams(workflow, state_manager, conn, filepool)
            self.loop(steps, conn, state_manager)
            filepool.join()
            for process in processes:
                conn.send(('stop', None, None))
                process.join()
        except WorkerError as e:
            sys.stderr.write(''.join(e.tb))
            filepool.terminate()
            for process in processes:
                process.terminate()

    def loop(self, steps, conn, state_manager):
        finalised = set()
        while not finalised.issuperset(steps):
            message, data = conn.recv()

            if message == 'data':
                step, state = data
                sys.stderr.write('master recieved data for {}\n'.format(step))
                if state.has_ended():
                    finalised.add(step)
                state_manager.drain_output(step, state)
                for consumer in state_manager.get_consumers(step):
                    if state_manager.can_run(consumer):
                        consumer_state = state_manager.get_state(consumer)
                        print('sending run to {}'.format(consumer))
                        conn.send(('run', consumer, consumer_state))
                        print('sent run to {}'.format(consumer))
                if state.can_run():
                    print('sending run to {}'.format(step))
                    conn.send(('run', step, state))
                    print('sent run to {}'.format(step))
            elif message == 'error':
                type_, value, tb = data
                raise WorkerError(value, tb)

    def start_processes(self):
        processes = []
        to_worker, from_worker = Pipe()
        for i in range(self.max_cpus):
            process = Process(target=worker, args=(i, from_worker))
            process.start()
            processes.append(process)
        return processes, to_worker

    def initialise_streams(self, workflow, state_manager, conn, filepool):
        for entity_type in workflow.provided_entities:
            if entity_type not in workflow.graph:
                continue
            entity = [filepool.get_file_manager()] if entity_type.name == 'filepool' else\
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
