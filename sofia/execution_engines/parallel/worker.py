import sys


def worker(id_, conn):
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
        message, step, state = conn.recv()
        sys.stderr.write(' worker {} recieved "{}" for {}\n'.format(id_, message, step))

        if message == 'run':
            state.run()
            conn.send((step, state))
        elif message == 'stop':
            break
        else:
            raise ValueError('unknown message to worker: {}'.format(message))
