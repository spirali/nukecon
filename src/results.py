
import chart

GAMMA_LIMITS = [ 30,   90,    150,   210,  270,   330, 9999 ]
GAMMA_NAMES = [ "sp", "+sc", "+ac", "ap", "-ac", "-sc", "sp" ]

DIRECTION_LIMITS = [ 45, 135, 225, 315 ]
DIRECTION_NAMES = [ "North", "East", "South", "West" ]


class Result:

    def __init__(self, structure):
        self.structure = structure
        self.gamma = None
        self.p = None

    @property
    def dir_index(self):
       for i, limit in enumerate(DIRECTION_LIMITS):
            if self.p < limit:
                return i
       return 0

    @property
    def gamma_index(self):
        for i, limit in enumerate(GAMMA_LIMITS):
            if self.gamma < limit:
                return i
        else:
            raise Exception("Invalid value")

    @property
    def dir_name(self):
        return DIRECTION_NAMES[self.dir_index]

    @property
    def gamma_name(self):
        return GAMMA_NAMES[self.gamma_index]


def group_by(lst, fn, sort_key=None, sort=True, flat=False, base=None):
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
    if not sort_key and not sort:
        return results
    results = list(results.items())
    if sort_key:
        results.sort(key=lambda item: sort_key(item[0]))
    elif sort:
        results.sort(key=lambda item: item[0])
    if flat:
        return [ values for key, values in results ]
    return results

def pc_fn(total):
    if total == 0:
        return lambda value: 0.0
    return lambda value: value * 100.0 / total

def percent(value, total):
    if total == 0:
        return 0.0
    return value * 100.0 / total

def process_results(analysis):
    results = analysis.results

    results_by_structures = group_by(
            results,
            lambda result: result.structure,
            lambda structure: structure.id)



    without_residue = analysis.structures.size - \
                      len(results_by_structures)

    dir_counts = list(map(len, group_by(results,
                                   lambda result: result.dir_index,
                                   base=range(len(DIRECTION_NAMES)),
                                   flat=True)))

    dir_counts_pc = list(map(pc_fn(sum(dir_counts)), dir_counts))

    gamma_values = [ r.gamma for r in results ]
    p_values = [ r.p for r in results ]

    data = [ [ len([ r for r in results
                     if r.dir_index == j and r.gamma_index == i ])
               for j in range(len(DIRECTION_NAMES)) ]
               for i in range(len(GAMMA_NAMES)) ]

    names = [ "{0} {1}".format(d, g)
              for d in DIRECTION_NAMES
              for g in GAMMA_NAMES ]

    sums = [ sum(row) for row in data ]
    total = sum(sums)

    table = [ [ percent(data[i][j], total)
                for j in range(len(DIRECTION_NAMES)) ]
                for i in range(len(GAMMA_NAMES)) ]

    values = [ table[i][j]
              for j in range(len(DIRECTION_NAMES))
              for i in range(len(GAMMA_NAMES)) ]

    table_rel = [ [ percent(data[i][j], sums[i])
                for j in range(len(DIRECTION_NAMES)) ]
                for i in range(len(GAMMA_NAMES)) ]

    values_rel = [ table_rel[i][j]
              for j in range(len(DIRECTION_NAMES))
              for i in range(len(GAMMA_NAMES)) ]



    return {
        "total" : total,
        "results_by_structures" : results_by_structures,
        "rejected" : analysis.rejected,
        "without_residue" : without_residue,
        "dir_counts" : zip(DIRECTION_NAMES, dir_counts, dir_counts_pc),
        "dir_counts_img" :
                chart.make_web_png(chart.make_barplot(
                    "Distribution of conformations",
                    "% of conformations",
                    DIRECTION_NAMES, dir_counts_pc,
                    figsize=(8, 1))),
        "dir_names" : DIRECTION_NAMES,
        "polar_chart" :
            chart.make_web_png(chart.make_polar_chart(
                "??? Title",
                gamma_values, p_values)),
        "sugar_table" : zip(GAMMA_NAMES, table),
        "sugar_chart" :
            chart.make_web_png(chart.make_barplot(
                "Conformations of sugar ring and C4-C5",
                "% of conformations",
                names, values,
                figsize=(8, 6))),
            "sugar_rel_table" : zip(GAMMA_NAMES, table_rel),
            "sugar_rel_chart" :
                chart.make_web_png(chart.make_barplot(
                    "Percentage within individual conformations",
                    "% within individual conformations",
                    names, values_rel,
                    figsize=(8, 6))),
    }

    """
    def percents(lst, s=None):
        if s is None:
            s = sum(lst)
        if s == 0:
            return [ 0.0 ] * len(lst)
        return [ i * 100 / s for i in lst ]

    sums = [ sum(row) for row in self.data ]
    total = sum(sums)

    names = [ "{0} {1}".format(d, g)
              for d in DIRECTION_NAMES
              for g in GAMMA_NAMES ]

    values = [ self.data[i][j]
                  for i in range(len(DIRECTION_NAMES))
                  for j in range(len(GAMMA_NAMES)) ]

    table = [ [ "{0} ({1:.2f}%) ".format(self.data[i][j],
                                      self.data[i][j] * 100 / total
                                      if total > 0 else 0.0)
               for i in range(len(DIRECTION_NAMES)) ]
               for j in range(len(GAMMA_NAMES)) ]

    values_rel = [ self.data[i][j] / sums[i] if sums[i] > 0 else 0.0
                  for i in range(len(DIRECTION_NAMES))
                  for j in range(len(GAMMA_NAMES)) ]

    table_rel = [ [ "{0} ({1:.2f}%) ".format(self.data[i][j],
                                         self.data[i][j] * 100 / sums[i]
                                         if sums[i] > 0 else 0.0)
               for i in range(len(DIRECTION_NAMES)) ]
               for j in range(len(GAMMA_NAMES)) ]

    return {
            "cf_size" : total,
            "cf_dirs" : zip(DIRECTION_NAMES,
                            self.direction_counts,
                            percents(self.direction_counts)),
            "cf_dirs_chart" :
                chart.make_web_png(chart.make_barplot(
                    "Distribution of conformations",
                    "# of conformations",
                    DIRECTION_NAMES, self.direction_counts,
                    figsize=(8, 1))),
            "rejected" : self.rejected,
            "dir_names" : DIRECTION_NAMES,
            "sugar_table" : zip(GAMMA_NAMES, table),
            "sugar_chart" :
                chart.make_web_png(chart.make_barplot(
                    "Conformations of sugar ring and C4-C5",
                    "# of conformations",
                    names, values,
                    figsize=(8, 6))),
            "sugar_rel_table" : zip(GAMMA_NAMES, table_rel),
            "sugar_rel_chart" :
                chart.make_web_png(chart.make_barplot(
                    "Percentage within individual conformations",
                    "% within individual conformations",
                    names, values_rel,
                    figsize=(8, 6))),

    }
    """


