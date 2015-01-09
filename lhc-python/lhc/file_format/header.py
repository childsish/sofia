def getSequenceId(name):
    name = name.strip().split()[0].lower()
    if name.startswith('chromosome'):
        return name[10:].strip()
    elif name.startswith('chr'):
        return name[3:].strip().upper()
    elif name.isdigit():
        if name == '6':
            return 'C'
        elif name == '7':
            return 'M'
        return name
    elif name.startswith('m'):
        return 'M'
    elif name.startswith('c'):
        return 'C'
    else:
        raise ValueError('Unrecognised sequence name: %s'%name)
