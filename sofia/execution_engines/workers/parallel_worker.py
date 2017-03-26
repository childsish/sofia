import sys


def parallel_worker(conn, steps):
    """
    All messages follow the form: <message>, <data>

    Valid messages
    --------------
    run, { 'step': <step_name>, 'input': <input_data> }
    finalise, { 'step': <step_name> }
    next, { 'step': <step_name> }
    stop, None
    """
    while True:
        message, data = conn.recv()
        sys.stderr.write(' worker recieved "{}" for {}\n'.format(message, data['step']))

        if message == 'run':
            steps[data['step']].send(('run', data['input']))
            conn.send(('running', {'step': data['step']}))
        elif message == 'finalise':
            steps[data['step']].send(('finalise', None))
            conn.send(('finalising', {'step': data['step']}))
        elif message == 'next':
            sys.stderr.write(' worker sending "next" to {}\n'.format(data['step']))
            steps[data['step']].send(('next', None))
            result = steps[data['step']].recv()
            conn.send(result)
            sys.stderr.write(' worker recieved "{}" from {}\n'.format(result[0], data['step']))
        elif message == 'stop':
            conn.send(('stopped', None))
            break
        else:
            raise ValueError('unknown message to worker: {}'.format(message))
