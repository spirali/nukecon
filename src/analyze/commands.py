from analyze import pdbquery
from base.structure import StructureList
import Bio.PDB as pdb
from analyze.analysis import Analysis
import base.paths as paths
from base import utils

import time
import logging
import datetime
import os

def ensure_data_dir():
    paths.makedir_if_not_exists(paths.DATA)

def get_summary_filename(component):
    return os.path.join(paths.DATA,
                        "summary-{0}.xml".format(component))

def get_results_filename(component):
    return os.path.join(paths.DATA,
                        "results-{0}.xml".format(component))

def load_summary(component):
    return StructureList(xmlfile=get_summary_filename(component))

def save_summary(component, structures):
    ensure_data_dir()
    structures.save(get_summary_filename(component))

def get_template(name):
    loader = jinja2.FileSystemLoader(paths.TEMPLATES)
    env = jinja2.Environment(loader=loader)
    return env.get_template(name)


def run_update(component):
    old_structures = load_summary(component)
    logging.info("Downloading list of structures with component %s ...",
                 component)
    pdb_ids = pdbquery.get_pdb_ids_by_component(component)
    if not pdb_ids:
        logging.warn("No structures found")
        return
    logging.info("%s structures found. Downloading report ...", len(pdb_ids))
    report_data = pdbquery.get_report(pdb_ids,
                                      ("structureId",
                                       "chainId",
                                       "structureTitle",
                                       "compound",
                                       "resolution",
                                       "experimentalTechnique",
                                       "ecNo"))
    report_rows = utils.group_by(
            report_data, lambda row: row[0], sort=True)
    new_structures = StructureList(datarows=report_rows)
    new, removed = new_structures.compare(old_structures)
    if new > 0:
        logging.info("There is %s new structures", new)
    else:
        logging.info("There is no new structure")
    if removed > 0:
        logging.warn("%s structures is no longer at the server", removed)

    save_summary(component, new_structures)

def run_summary(component):
    structures = load_summary(component)
    structures.fill_download_info()
    resolution_stats = structures.make_resolution_stats()
    downloaded_size = len(structures.filter_downloaded())
    imgs = []

    fig = chart.make_barplot("Resolution of structures", "# structures",
            [ "N/A", "<= 1", "(1, 2]", "(2, 3]", "> 3" ], resolution_stats)
    imgs.append(chart.make_web_png(fig))

    fig = chart.make_pie("",
            [ "Downloaded", "Not downloaded"] ,
            [ downloaded_size, len(structures) - downloaded_size],
            colors=("green", "gray"))
    imgs.append(chart.make_web_png(fig))

    template = get_template("summary.html")
    report_html = template.render(
            imgs=imgs,
            structures=structures.structures,
            component=component.upper(),
            date=datetime.datetime.now())
    with open("summary-{0}.html".format(component), "w") as f:
        f.write(report_html)
    logging.info("Summary of %s structures written as 'summary-%s.html'",
            len(structures),
            component)

def run_download(component, max_resolution):
    structures = load_summary(component).filter(
            max_resolution=max_resolution)
    structures.fill_download_info()
    structures = structures.filter_not_downloaded()

    pdb_list = pdb.PDBList()
    logging.info("Downloading %s structures ...", len(structures))

    for i, id in enumerate(structures.get_ids()):
        path = os.path.join(paths.DATA, id[:2].lower())
        pdb_list.retrieve_pdb_file(id, pdir=path)
        if i % 3 == 2:
            # To prevent of being kicked by too many connections
            time.sleep(5)

def run_analysis(component):
    structures = load_summary(component)
    structures
    structures.fill_download_info()
    structures = structures.filter_downloaded()

    analysis = Analysis(structures, component)
    analysis.run()

    structures.save(get_results_filename(component))
