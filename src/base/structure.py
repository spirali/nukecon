import logging
import os.path
from base import paths
from base import utils

import xml.etree.ElementTree as xml
import itertools
import copy

GAMMA_LIMITS = [ 30,   90,    150,   210,  270,   330, 9999 ]
GAMMA_NAMES = [ "sp", "+sc", "+ac", "ap", "-ac", "-sc", "sp" ]

DIRECTION_LIMITS = [ 45, 135, 225, 315 ]
DIRECTION_NAMES = [ "North", "East", "South", "West" ]


class Result:

    def __init__(self):
        self.gamma = None
        self.p = None
        self.tm = None
        self.synanti = None
        self.mixed_results = 1

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

    def to_element(self):
        e = xml.Element("result")
        e.set("gamma", str(self.gamma))
        e.set("p", str(self.p))
        e.set("tm", str(self.tm))
        e.set("synanti", str(self.synanti))
        return e

    @classmethod
    def from_element(cls, e):
        result = cls()
        result.gamma = float(e.get("gamma"))
        result.p = float(e.get("p"))
        result.tm = float(e.get("tm"))
        result.synanti = float(e.get("synanti"))
        return result


class Chain:

    def __init__(self, id):
        self.id = id
        self.ec_numbers = []
        self.compound = None
        self.results = []

    def add_result(self, result):
        self.results.append(result)

    @property
    def ec_numbers_str(self):
        return ", ".join(self.ec_numbers)

    def to_element(self):
        e = xml.Element("chain")
        e.set("id", self.id)
        e.set("compound", self.compound)
        for ec_no in self.ec_numbers:
            e2 = xml.Element("ec-number")
            e2.text = str(ec_no)
            e.append(e2)
        for result in self.results:
            e.append(result.to_element())
        return e

    @classmethod
    def from_element(cls, element):
        chain = cls(element.get("id"))
        chain.ec_numbers = [ e.text for e in element.findall("ec-number") ]
        chain.compound = element.get("compound")
        chain.results = [ Result.from_element(e) for e in element.findall("result") ]
        return chain

def avg_results(results):
    r = Result()
    l = len(results)
    r.mixed_results = l
    r.gamma = (sum(s.gamma for s in results) % 360.0) / l
    r.tm = (sum(s.tm for s in results) % 360.0) / l
    r.p = (sum(s.p for s in results) % 360.0) / l
    return r

def angle_diff(a, b):
    d = abs(a - b)
    if d > 180.0:
        return d - 180.0
    else:
        return d

def join_chains(chains, angle_limit):
    def key(v):
        return v[1].p

    results = []
    for c in chains:
        results.extend((c, r) for r in c.results)

    if not results:
        return results

    results.sort(key=key)

    for n in xrange(1, len(results) + 1):
        best_angle = 360.0
        best_partition = None
        for partition in utils.make_partitions(results, n):
            angle = 0
            for s in partition:
                a = sum(angle_diff(s[i-1][1].p, s[i][1].p) for i in xrange(1, len(s)))
                if a > angle:
                    angle = a
            if angle < best_angle:
                best_angle = angle
                best_partition = partition
        if best_angle <= angle_limit:
            break

    result = []
    for s in best_partition:
        chains = list(set(c for c, r in s))
        chains.sort(key=lambda c: c.id)
        chain = Chain(",".join(c.id for c in chains))
        chain.results = [ avg_results([r for c, r, in s]) ]
        chain.ec_numbers = chains[0].ec_numbers
        chain.compound = chains[0].compound
        result.append(chain)
    return result


class Structure:

    def __init__(self, id):
        self.id = id
        self.downloaded = False
        self.resolution = None
        self.exp_technique = None
        self.title = None
        self.chains = []

    @property
    def filename(self):
        return os.path.join(paths.DATA,
                            self.id[:2].lower(),
                            "pdb{0}.ent".format(self.id.lower()))

    def get_chain(self, id):
        for chain in self.chains:
            if chain.id == id:
                return chain

    def join_chains(self, angle_limit):
        s = copy.copy(self)
        if self.chains:
            s.chains = join_chains(self.chains, angle_limit)
        return s

    def to_element(self):
        e = xml.Element("structure")
        e.set("id", str(self.id))
        if self.resolution is not None:
            e.set("resolution", str(self.resolution))
        e.set("exp-technique", self.exp_technique)
        e.set("title", self.title)
        for chain in self.chains:
            e.append(chain.to_element())
        return e

    def fill_download_info(self):
        self.downloaded = os.path.isfile(self.filename)

    def strip_empty_chains(self):
        s = copy.copy(self)
        s.chains = [ chain for chain in self.chains if chain.results ]
        return s

    @classmethod
    def from_datarow(cls, row):
        id, chains = row
        id, chain_id, title, compound, resolution, exp_technique, ec_no \
            = chains[0]
        s = cls(id)
        try:
            s.resolution = float(resolution)
        except ValueError:
            s.resolution = None
        s.exp_technique = exp_technique
        s.title = title

        for c in chains:
            id, chain_id, t, c, resolution, exp_technique, ec_no = c
            assert t == title
            chain = Chain(chain_id)
            chain.compound = c
            if ec_no:
                chain.ec_numbers = ec_no.split("#")
            s.chains.append(chain)

        return s

    @classmethod
    def from_element(cls, element):
        s = cls(element.get("id"))
        resolution = element.get("resolution", None)
        if resolution is not None:
            s.resolution = float(resolution)
        s.exp_technique = element.get("exp-technique")
        s.title = element.get("title", None)
        s.chains = [ Chain.from_element(e) for e in element.findall("chain") ]
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
            except Exception:
                logging.debug("File with structures not found")
                return
            for e in tree.getroot():
                self.structures.append(Structure.from_element(e))

    def get_missing(self, slist):
        my = set(s.id for s in self.structures)
        other = set(s.id for s in slist.structures)
        diff = other - my
        result = []
        for s in slist.structures:
            if s.id in diff:
                result.append(s)
        return StructureList(structures=result)

    def add(self, slist):
        self.structures.extend(slist.structures)

    def save(self, filename):
        root = xml.Element("structures")

        for s in self.structures:
            root.append(s.to_element())

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

    def filter(self, max_resolution=None):
        structures = self.structures
        if max_resolution is not None:
            structures = (s for s in structures
                          if s.resolution and
                             s.resolution <= max_resolution)
        return StructureList(structures=list(structures))

    def filter_downloaded(self):
        structures = [ s for s in self.structures if s.downloaded ]
        return StructureList(structures=structures)

    def filter_not_downloaded(self):
        structures = [ s for s in self.structures if not s.downloaded ]
        return StructureList(structures=structures)

    def fill_download_info(self):
        for s in self.structures:
            s.fill_download_info()

    def filter_with_results(self):
        structures = [ s for s in self.structures
                       if any(c.results for c in s.chains) ]
        return StructureList(structures=structures)

    def join_chains(self, angle_limit):
        structures = [ s.join_chains(angle_limit) for s in self.structures ]
        return StructureList(structures=structures)

    def strip_empty_chains(self):
        return StructureList(
                structures=[ s.strip_empty_chains() for s in self.structures ])

    @property
    def chains(self):
        return itertools.chain.from_iterable(s.chains for s in self.structures)

    @property
    def results(self):
        return itertools.chain.from_iterable(c.results for c in self.chains)

    def make_table(self):
        return []

    def __iter__(self):
        return iter(self.structures)

    def __len__(self):
        return len(self.structures)
