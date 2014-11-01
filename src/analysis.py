
import Bio.PDB as PDB
import math
import chart
import logging

GAMMA_LIMITS = [ 30,   90,    150,   210,  270,   330, 9999 ]
GAMMA_NAMES = [ "sp", "+sc", "+ac", "ap", "-ac", "-sc", "sp" ]

DIRECTION_LIMITS = [ 45, 135, 225, 315 ]
DIRECTION_NAMES = [ "North", "East", "South", "West" ]


class Analysis:

    atom_names = [ "C4'", "O4'", "C1'", "C2'", "C3'", "C5'", "O5'" ]

    def __init__(self, structures, component):
        self.structures = structures
        self.component = component

        self.direction_counts = [0] * len(DIRECTION_NAMES)

        # 2d Table len(direction_names) * len(gamma_names)
        self.data = [ [0] * len(GAMMA_NAMES) for n in DIRECTION_NAMES]

    def run(self):
        parser = PDB.PDBParser(PERMISSIVE=5)
        for structure in self.structures:
            #filename = os.path.join(self.ligand_type, "pdb{}.ent".format(ligand))
            structure = parser.get_structure(structure.id, structure.filename)
            self.process_structure(structure)

    def process_structure(self, structure):
        for model in structure:
            for chain in model:
                for residue in chain:
                    if residue.resname.lower() == self.component:
                        self.process_residue(residue)

    def get_results(self):
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

    def process_residue(self, residue):
        if not all(name in residue for name in self.atom_names):
            # TODO: How to handle this errors?
            print("The structure", residue,
                    "does not contain one of essential atoms:",
                    " ".join(name for name in self.atom_names
                                  if name not in residue))
            return
        vectors = [ residue[name].get_vector() for name in self.atom_names ]
        vs = []

        for i in range(5):
            v1 = vectors[i % 5]
            v2 = vectors[(i + 1) % 5]
            v3 = vectors[(i + 2) % 5]
            v4 = vectors[(i + 3) % 5]
            v = math.degrees(PDB.calc_dihedral(v1, v2, v3, v4))
            vs.append(v)
            logging.debug("v{0}={1:.2f}°".format(i + 1, v))

        gamma = math.degrees(
                    PDB.calc_dihedral(vectors[6], vectors[5], vectors[0], vectors[4]))
        if gamma < 0:
            gamma += 360
        logging.debug("gamma = {0:.2f}°".format(gamma))

        y = vs[4]+vs[1]-vs[3]-vs[0]
        x = 2*vs[2]*(math.sin(math.pi/5)+math.sin(math.pi/2.5))
        p1 = math.atan2(y,x)
        p = 180/math.pi*p1
        tm = vs[2]/math.cos(p1)

        if p < 0:
            p += 360

        logging.debug('\nPhase angle of pseudorotation P = {0:.2f}°'.format(p))
        logging.debug('Maximum degree of pucker tm = {0:.2f}°'.format(tm))

        for i, limit in enumerate(GAMMA_LIMITS):
            if gamma < limit:
                gamma_id = i
                break
        else:
            raise Exception("Internal error")

        for i, limit in enumerate(DIRECTION_LIMITS):
            if p < limit:
                direction_id = i
                break
        else:
            direction_id = 0 # North

        self.direction_counts[direction_id] += 1
        self.data[direction_id][gamma_id] += 1
