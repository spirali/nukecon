import io
import csv

def group_by(lst, fn, sort_key=None, sort=False,
             only_values=False, base=None, as_dict=False):
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
    if as_dict:
        return results
    results = list(results.items())
    if sort_key:
        results.sort(key=lambda item: sort_key(item[0]))
    elif sort:
        results.sort(key=lambda item: item[0])
    if only_values:
        return [ values for key, values in results ]
    return results


def combinations(lst, size):
    if size == 1:
        return [ [a] for a in lst ]

    result = []
    for i, a in enumerate(lst):
        f = [a]
        result.extend(f + l for l in combinations(lst[i+1:], size - 1))
    return result


# For examples see utils_test.py
def make_partitions(lst, size):
    assert size > 0 and size <= len(lst)
    if size == 1:
        return [ [ lst ] ]
    result = []
    for c in combinations(range(len(lst)), size):
        paritition = [ lst[c[-1]:] + lst[:c[0]] ]
        for i in xrange(1, len(c)):
            paritition.append(lst[c[i - 1]:c[i]])
        result.append(paritition)
    return result


def table_to_csv(table):
    s = io.BytesIO()
    csv.writer(s).writerows(table)
    return s.getvalue()

