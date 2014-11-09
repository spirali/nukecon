
def group_by(lst, fn, sort_key=None, sort=False, only_values=False, base=None):
    results = {}
    if base is not None:
        for key in base:
            results[key] = []
    for item in lst:
        key = fn(item)
        values = results.get(key)
        if values:
            values.append(item)
        else:
            results[key] = [ item ]
    results = list(results.items())
    if sort_key:
        results.sort(key=lambda item: sort_key(item[0]))
    elif sort:
        results.sort(key=lambda item: item[0])
    if only_values:
        return [ values for key, values in results ]
    return results
