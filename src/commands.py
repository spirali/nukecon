import pdbquery
import chart
from structure import StructureList
import Bio.PDB as pdb
from analysis import Analysis
from results import process_results

import time
import paths
import logging
import jinja2
import datetime
import os

def ensure_data_dir():
    paths.makedir_if_not_exists(paths.DATA)

def get_summary_filename(query):
    return os.path.join(paths.DATA,
                        "summary-{0}.xml".format(query.component))

def load_summary(query):
    return StructureList(xmlfile=get_summary_filename(query))

def save_summary(query, structures):
    ensure_data_dir()
    structures.save_summary(get_summary_filename(query))

def get_template(name):
    loader = jinja2.FileSystemLoader(paths.TEMPLATES)
    env = jinja2.Environment(loader=loader)
    return env.get_template(name)


def run_update(query):
    old_structures = load_summary(query)
    logging.info("Downloading list of structures with component %s ...",
                 query.component)
    pdb_ids = pdbquery.get_pdb_ids_by_component(query.component)
    if not pdb_ids:
        logging.warn("No structures found")
        return
    logging.info("%s structures found. Downloading report ...", len(pdb_ids))
    report_data = pdbquery.get_report(pdb_ids,
                                      ("structureId",
                                       "resolution",
                                       "experimentalTechnique"))
    new_structures = StructureList(datarows=report_data)

    new, removed = new_structures.compare(old_structures)
    if new > 0:
        logging.info("There is %s new structures", new)
        logging.info("Use command 'summary' to see them")
    else:
        logging.info("There is no new structure")
    if removed > 0:
        logging.warn("%s structures is no longer at the server", removed)

    save_summary(query, new_structures)

def run_summary(query):
    structures = load_summary(query).filter_by_query(query)
    structures.fill_download_info()
    resolution_stats = structures.make_resolution_stats()
    downloaded_size = structures.filter_downloaded().size
    imgs = []

    fig = chart.make_barplot("Resolution of structures", "# structures",
            [ "N/A", "<= 1", "(1, 2]", "(2, 3]", "> 3" ], resolution_stats)
    imgs.append(chart.make_web_png(fig))

    fig = chart.make_pie("",
            [ "Downloaded", "Not downloaded"] ,
            [ downloaded_size, structures.size - downloaded_size],
            colors=("green", "gray"))
    imgs.append(chart.make_web_png(fig))

    template = get_template("summary.html")
    report_html = template.render(
            filters=query.get_filter_names(),
            imgs=imgs,
            structures=structures.structures,
            component=query.component.upper(),
            date=datetime.datetime.now())
    with open("summary-{0}.html".format(query.component), "w") as f:
        f.write(report_html)
    logging.info("Summary of %s structures written as 'summary-%s.html'",
            structures.size,
            query.component)

def run_download(query):
    structures = load_summary(query).filter_by_query(query)
    structures.fill_download_info()
    structures = structures.filter_not_downloaded()

    pdb_list = pdb.PDBList()
    logging.info("Downloading %s structures ...", structures.size)

    for i, id in enumerate(structures.get_ids()):
        path = os.path.join(paths.DATA, id[:2].lower())
        pdb_list.retrieve_pdb_file(id, pdir=path)
        if i % 3 == 2:
            # To prevent of being kicked by too many connections
            time.sleep(5)

def run_analysis(query):
    structures = load_summary(query).filter_by_query(query)
    structures.fill_download_info()
    structures = structures.filter_downloaded()

    analysis = Analysis(structures, query.component)
    analysis.run()

    template = get_template("report.html")
    report_html = template.render(
            structures=structures,
            component=query.component.upper(),
            date=datetime.datetime.now(),
            **process_results(analysis))
    with open("report-{0}.html".format(query.component), "w") as f:
        f.write(report_html)
    logging.info("Report of analysis was written as 'report-%s.html'",
                 query.component)


