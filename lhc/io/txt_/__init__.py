def extract_typed_columns(line, columns=((1, str),), sep='\t'):
    parts = line.rstrip('\r\n').split(sep)
    return (t(parts[i]) for i, t in columns)
