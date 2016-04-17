
import chart
from base import utils
from base import paths

import os
from base.structure import StructureList, GAMMA_NAMES, DIRECTION_NAMES


def pc_fn(total):
    if total == 0:
        return lambda value: 0.0
    return lambda value: value * 100.0 / total


def percent(value, total):
    if total == 0:
        return 0.0
    return value * 100.0 / total


def get_by_form(component, form):
    filename =  os.path.join(paths.DATA,
                             "results-{0}.xml".format(component))
    structures = StructureList(xmlfile=filename).filter(
            max_resolution=form.max_resolution.data)
    if form.join_results.data == 'join':
        structures = structures.join_chains(form.join_angle.data)
    structures = structures.filter_with_results()
    return structures


def make_table(component, form):
    structures = get_by_form(component, form)
    results = [[
        "id",
        "title",
        "chain_id",
        "compound",
        "ec_numbers",
        "dir_name",
        "gamma_name",
        "p",
        "tm",
        "synanti",
        "mixed_results"
    ]]
    for structure in structures:
        for chain in structure.chains:
            for result in chain.results:
                row = [structure.id,
                       structure.title,
                       chain.id,
                       chain.compound,
                       chain.ec_numbers_str,
                       result.dir_name[0],
                       result.gamma_name,
                       result.p,
                       result.tm,
                       result.synanti,
                       result.mixed_results]
                results.append(row)
    return results


def get_results(component, form):
    structures = get_by_form(component, form)
    results = list(structures.results)

    if len(results) == 0:
        return {}

    p_values = [ r.p for r in results ]
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

    dir_counts = list(map(len, utils.group_by(
        results, lambda result: result.dir_index,
        base=range(len(DIRECTION_NAMES)), only_values=True)))

    dir_counts_pc = list(map(pc_fn(sum(dir_counts)), dir_counts))

    return { "structures" : structures,
             "results" : results,
             "polar_chart" :
                chart.make_web_png(chart.make_polar_chart(
                    "??? Title",
                    p_values, tm_values, "P", "$\\nu_{max}$")),
            "dir_names" : DIRECTION_NAMES,
            "dir_counts" : zip(DIRECTION_NAMES, dir_counts, dir_counts_pc),
            "dir_counts_img" :
                    chart.make_web_png(chart.make_barplot(
                        "Distribution of conformations",
                        "% of conformations",
                        DIRECTION_NAMES, dir_counts_pc,
                        figsize=(8, 1))),
            "sugar_table" : zip(GAMMA_NAMES, table),
            "sugar_chart" :
                chart.make_web_png(chart.make_barplot(
                    "Conformations of sugar ring and C4-C5",
                    "% of conformations",
                    names, values,
                    figsize=(8, 6))),
           }
