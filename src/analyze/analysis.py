
from base.structure import Result

import Bio.PDB as PDB
import math
import logging


class Analysis:

    atom_names = [ "C4'", "O4'", "C1'", "C2'", "C3'", "C5'", "O5'" ]

    def __init__(self, structures, component):
        self.structures = structures
        self.component = component
        self.rejected = []
        self.results = []

    def run(self):
        parser = PDB.PDBParser(PERMISSIVE=5)
        for structure in self.structures:
            pdb_structure = parser.get_structure(structure.id, structure.filename)
            self.process_structure(structure, pdb_structure)

    def process_structure(self, structure, pdb_structure):
        for pdb_model in pdb_structure:
            for pdb_chain in pdb_model:
                for residue in pdb_chain:
                    if residue.resname.lower() == self.component:
                        self.process_residue(structure, pdb_structure, pdb_chain, residue)

    def process_residue(self, structure, pdb_structure, pdb_chain, residue):
        residue_atoms = [ atom.get_name() for atom in residue ]
        if not all(name in residue_atoms for name in self.atom_names):
            missing_atoms = [ name for name in self.atom_names
                                   if name not in residue_atoms ]
            self.rejected.append((pdb_structure.id,
                                  pdb_chain.id,
                                  "Does not contain " + ",".join(
                                      missing_atoms)))
            logging.debug("Rejected %s", self.rejected[-1])
            return
        vectors = [ residue[name].get_vector() for name in self.atom_names ]
        print structure, pdb_structure
        if residue.has_id("N9") and residue.has_id("C4"):
            v8 = residue["C4"].get_vector()
            v9 = residue["N9"].get_vector()
        elif residue.has_id("N1"):
            v8 = residue["N1"].get_vector()
            v9 = residue["C2"].get_vector()
        else:
            logging.debug("Rejected %s (no N9/C4 or N1)", structure)
            return

        vs = []

        for i in range(5):
            v1 = vectors[i % 5]
            v2 = vectors[(i + 1) % 5]
            v3 = vectors[(i + 2) % 5]
            v4 = vectors[(i + 3) % 5]
            v = math.degrees(PDB.calc_dihedral(v1, v2, v3, v4))
            vs.append(v)
            logging.debug("v{0}={1:.2f}".format(i + 1, v))


        gamma = math.degrees(
                    PDB.calc_dihedral(vectors[6], vectors[5], vectors[0], vectors[4]))
        if gamma < 0:
            gamma += 360
        logging.debug("gamma = {0:.2f}".format(gamma))

        y = vs[4]+vs[1]-vs[3]-vs[0]
        x = 2*vs[2]*(math.sin(math.pi/5)+math.sin(math.pi/2.5))
        p1 = math.atan2(y,x)
        p = 180/math.pi*p1
        tm = vs[2]/math.cos(p1)

        if p < 0:
            p += 360

        logging.debug('\nPhase angle of pseudorotation P = {0:.2f}'.format(p))
        logging.debug('Maximum degree of pucker tm = {0:.2f}'.format(tm))

        synanti = math.degrees(
                PDB.calc_dihedral(vectors[1], vectors[2], v8, v9))

        result = Result()
        result.gamma = gamma
        result.p = p
        result.tm = tm
        result.synanti = synanti
        structure.get_chain(pdb_chain.id).add_result(result)
