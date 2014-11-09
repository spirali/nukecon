
import xml.etree.ElementTree as xml
import logging
import os.path
import paths

class Structure:

    def __init__(self, id):
        self.id = id
        self.downloaded = False
        self.resolution = None
        self.exp_technique = None
        self.ecn = None

    @property
    def filename(self):
        return os.path.join(paths.DATA,
                            self.id[:2].lower(),
                            "pdb{0}.ent".format(self.id.lower()))

    def to_xml(self):
        e = xml.Element("structure")
        e.set("id", str(self.id))
        if self.resolution is not None:
            e.set("resolution", str(self.resolution))
        e.set("exp-technique", self.exp_technique)
        if self.ecn is not None:
            e.set("ecn", self.ecn)
        return e

    def fill_download_info(self):
        self.downloaded = os.path.isfile(self.filename)

    @classmethod
    def from_datarow(cls, row):
        id, resolution, exp_technique = row
        s = cls(id)
        try:
            s.resolution = float(resolution)
        except ValueError:
            s.resolution = None
        s.exp_technique = exp_technique
        return s

    @classmethod
    def from_element(cls, element):
        s = cls(element.get("id"))
        resolution = element.get("resolution", None)
        if resolution is not None:
            s.resolution = float(resolution)
        s.exp_technique = element.get("exp-technique")
        s.ecn = element.get("ecn")
        return s


class StructureList:

    def __init__(self, datarows=None, xmlfile=None, structures=None):
        if structures is None:
            structures = []

        self.structures = structures

        if datarows is not None:
            for row in datarows:
                self.structures.append(Structure.from_datarow(row))

        if xmlfile is not None:
            try:
                tree = xml.parse(xmlfile)
            except FileNotFoundError:
                logging.debug("File with structures not found")
                return
            for e in tree.getroot():
                self.structures.append(Structure.from_element(e))

    def save_summary(self, filename):
        root = xml.Element("structures")

        for s in self.structures:
            root.append(s.to_xml())

        tree = xml.ElementTree(root)
        tree.write(filename)

    def get_ids(self):
        return [ s.id for s in self.structures]

    def compare(self, other):
        my_ids = frozenset(self.get_ids())
        other_ids = frozenset(other.get_ids())
        return len(my_ids - other_ids), len(other_ids - my_ids)

    def make_resolution_stats(self):
        resolution_stats = [ 0, 0, 0, 0, 0 ]

        for s in self.structures:
            if s.resolution is None:
                resolution_stats[0] += 1
            elif s.resolution <= 1.0:
                resolution_stats[1] += 1
            elif s.resolution <= 2.0:
                resolution_stats[2] += 1
            elif s.resolution <= 3.0:
                resolution_stats[3] += 1
            else:
                resolution_stats[4] += 1
        return resolution_stats

    def filter_by_query(self, query):
        structures = self.structures
        if query.resolution_max is not None:
            structures = (s for s in structures
                          if s.resolution and
                             s.resolution <= query.resolution_max)
        return StructureList(structures=list(structures))

    def filter_downloaded(self):
        structures = [ s for s in self.structures if s.downloaded ]
        return StructureList(structures=list(structures))

    def filter_not_downloaded(self):
        structures = [ s for s in self.structures if not s.downloaded ]
        return StructureList(structures=list(structures))

    def fill_download_info(self):
        for s in self.structures:
            s.fill_download_info()

    def __iter__(self):
        return iter(self.structures)

    def __len__(self):
        return len(self.structures)
