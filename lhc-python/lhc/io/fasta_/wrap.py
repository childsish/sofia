import argparse


def wrap(args):
    in_fhndl = open(args.input)
    out_fhndl = open(args.output, 'w')

    for line in wrap_input(in_fhndl, args.buffer_size, args.width):
        out_fhndl.write(line)
        out_fhndl.write('\n')

    in_fhndl.close()
    out_fhndl.close()


def wrap_input(fhndl, buffer_size, width):
    buffer = fhndl.read(buffer_size)
    while len(buffer) >= buffer_size:
        while '>' in buffer:
            header_index = buffer.index('>')
            tmp = ''.join(buffer[:header_index].split())
            if len(tmp) > width:
                for i in xrange(len(tmp) / width):
                    yield tmp[i * width:(i + 1) * width]
                yield tmp[(i + 1) * width:]
            else:
                yield tmp
            newline_index = buffer.find('\n', header_index)
            if newline_index == -1:
                break
            yield buffer[header_index:newline_index]
            buffer = buffer[newline_index + 1:]
        buffer = ''.join(buffer.split())
        if len(buffer) > width:
            for i in xrange(len(buffer) / width):
                yield buffer[i * width:(i + 1) * width]
            remainder = len(buffer) % width
            buffer = buffer[-remainder:]
        buffer += fhndl.read(buffer_size)
    buffer = ''.join(buffer.split())
    for i in xrange(len(buffer) / width - 1):
        yield buffer[i * width:(i + 1) * width]
    remainder = len(buffer) % width
    yield buffer[-remainder:]


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input')
    add_arg('output')
    add_arg('-b', '--buffer-size', default=2 ** 16, type=int,
            help='The number of bytes to read at a time.')
    add_arg('-w', '--width', default=80, type=int,
            help='The maximum length of a sequence line (default: 80).')
    parser.set_defaults(func=wrap)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
