from analyze import pdbquery
from base.structure import StructureList
import Bio.PDB as pdb
from analyze.analysis import Analysis
import base.paths as paths
from base import utils

import time
import logging
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

def load_results(component):
    return StructureList(xmlfile=get_results_filename(component))

def save_summary(component, structures):
    ensure_data_dir()
    structures.save(get_summary_filename(component))

def run_update(component):
    old_structures = load_summary(component)
    logging.info("Downloading list of structures with component %s ...",
                 component)
    pdb_ids = pdbquery.get_pdb_ids_by_component(component)
    if not pdb_ids:
        logging.warn("No structures found")
        return
    time.sleep(2)
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

    results = load_results(component)
    new_structures = results.get_missing(structures)
    logging.info("%s old results / %s new results", len(results), len(new_structures))

    analysis = Analysis(new_structures, component)
    analysis.run()

    results.add(new_structures)
    results.save(get_results_filename(component))
