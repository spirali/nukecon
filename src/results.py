
import chart
import utils

GAMMA_LIMITS = [ 30,   90,    150,   210,  270,   330, 9999 ]
GAMMA_NAMES = [ "sp", "+sc", "+ac", "ap", "-ac", "-sc", "sp" ]

DIRECTION_LIMITS = [ 45, 135, 225, 315 ]
DIRECTION_NAMES = [ "North", "East", "South", "West" ]


class Result:

    def __init__(self, structure):
        self.structure = structure
        self.gamma = None
        self.p = None
        self.tm = None

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

    results_by_structures = utils.group_by(
            results,
            lambda result: result.structure,
            sort_key=lambda structure: structure.id)

    without_residue = len(analysis.structures) - \
                      len(results_by_structures)

    dir_counts = list(map(len, utils.group_by(
        results, lambda result: result.dir_index,
        base=range(len(DIRECTION_NAMES)), only_values=True)))

    dir_counts_pc = list(map(pc_fn(sum(dir_counts)), dir_counts))

    gamma_values = [ r.gamma for r in results ]
    tm_values = [ r.tm for r in results ]

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
                gamma_values, tm_values, "$\\nu$", "tm")),
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
