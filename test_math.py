def calc(options):
    return list(map(lambda kv: kv[0] + ': ' + str(kv[1]), options.items()))