def calc(options):
    return '\n'.join(map(lambda kv: kv[0] + ': ' + str(kv[1]), options.items()))