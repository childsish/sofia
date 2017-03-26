import sys


def step_worker(step, pipe, max_entities):
    """
    All messages follow the form: <message>, <data>

    Valid messages
    --------------
    run, <input_data>
    finalise, None
    next, None
    stop, None
    """
    state = None
    while True:
        message, input = pipe.recv()
        if message == 'run':
            state = step.run(input, max_entities)
        elif message == 'finalise':
            state = step.finalise(max_entities)
        elif message == 'next':
            try:
                data = state.next()
                sys.stderr.write('  {}\n'.format(step.name))
                sys.stderr.write('  * {}\n'.format(', '.join(key.name for key in data)))
                sys.stderr.write('  *  {}\n'.format(', '.join(str(value) for value in data.values())))
                pipe.send(('data', {'step': step, 'data': data}))
            except StopIteration:
                pipe.send(('stop', {'step': step}))
                state = None
        elif message == 'stop':
            break
